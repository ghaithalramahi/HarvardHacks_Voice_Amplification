#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  4 16:18:33 2025

@author: ayskagadhwala
"""

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import numpy as np
import base64
from dsp.vad import VAD
from dsp.denoiser import Denoiser
from dsp.speaker_filter import SpeakerFilter
from dsp.tone import confident_voice
from dsp.amplify import apply_gain
from dsp.metrics import AudioMetrics
import io
import wave

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components globally
vad = None
denoiser = None
speaker_filter = None
metrics = AudioMetrics()
gain = 12.0  # Maximum amplification - increased for even more amplification
samplerate = 16000

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/flow')
def flow():
    with open('audio_flow_test.html', 'r', encoding='utf-8') as f:
        return f.read()

@socketio.on('connect')
def handle_connect():
    global vad, denoiser, speaker_filter
    print('Client connected')
    
    # Initialize components on first connection
    if vad is None:
        print("Initializing audio processing pipeline...")
        try:
            vad = VAD(mode=3, samplerate=samplerate)  # Mode 3 = strict (less noise, more precise)
            denoiser = Denoiser(model_name="master64", device="cpu")  # Master model for better denoising
            speaker_filter = SpeakerFilter(target_pitch_range=(100, 250), samplerate=samplerate)
            print("✓ Pipeline ready")
        except Exception as e:
            print(f"Warning: Some components failed to initialize: {e}")
            # Initialize with fallbacks
            vad = VAD(mode=3, samplerate=samplerate)  # Mode 3 = strict (less noise, more precise)
            denoiser = Denoiser(model_name="master64", device="cpu")  # Master model for better denoising
            speaker_filter = SpeakerFilter(target_pitch_range=(100, 250), samplerate=samplerate)
    
    emit('ready', {'message': 'Server ready to process audio'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('audio_data')
def handle_audio(data):
    """Process incoming audio chunks from browser"""
    try:
        # Decode base64 audio data
        audio_bytes = base64.b64decode(data['audio'])
        
        # Convert bytes to numpy array (assuming float32 PCM)
        audio = np.frombuffer(audio_bytes, dtype=np.float32)
        audio = audio.reshape(-1, 1)
        
        # Debug: Print audio info
        print(f"Audio shape: {audio.shape}, max: {np.max(np.abs(audio)):.4f}")
        
        # Check if speech detected
        try:
            frame_bytes = vad.float_to_bytes(audio)
            is_speech = vad.is_speech(frame_bytes) and np.max(np.abs(audio)) > 0.02
            print(f"VAD result: {vad.is_speech(frame_bytes)}, max_audio: {np.max(np.abs(audio)):.4f}, is_speech: {is_speech}")
        except Exception as vad_error:
            print(f"VAD error: {vad_error}")
            # Fallback: use simple amplitude threshold
            is_speech = np.max(np.abs(audio)) > 0.02
            print(f"Fallback VAD: is_speech: {is_speech}")
        
        if is_speech:
            try:
                # Check if target speaker
                is_target, pitch = speaker_filter.is_target_speaker(audio)
                
                if is_target:
                    # Process audio - Use denoiser output with improved amplifier
                    denoised = denoiser.process(audio, sr=samplerate)
                    
                    # Skip the aggressive tone enhancement for now
                    # enhanced = confident_voice(denoised, samplerate)
                    enhanced = denoised  # Use denoised audio directly
                    
                    # Apply improved gain processing
                    amplified = apply_gain(enhanced, gain)
                    
                    # Debug: Test with simple passthrough first
                    # amplified = audio  # Uncomment this line to test without processing
                    
                    # Debug: Test with very high amplification
                    # amplified = audio * 10.0  # Uncomment for extreme amplification test
                    
                    # Calculate metrics
                    rms = metrics.rms_energy(amplified)
                    snr = metrics.snr(denoised, audio)
                    vad_conf = metrics.vad_confidence(audio, vad, is_speech)
                    
                    # Convert back to bytes and base64
                    # Ensure amplified audio is in the right range
                    amplified_clipped = np.clip(amplified, -1.0, 1.0)
                    
                    # Debug: Print audio statistics
                    print(f"Audio stats - min: {np.min(amplified_clipped):.4f}, max: {np.max(amplified_clipped):.4f}, rms: {np.sqrt(np.mean(amplified_clipped**2)):.4f}")
                    
                    # Convert to int16 with proper scaling
                    amplified_int16 = (amplified_clipped * 32767).astype(np.int16)
                    output_bytes = amplified_int16.tobytes()
                    output_b64 = base64.b64encode(output_bytes).decode('utf-8')
                    
                    print(f"Sending audio back - size: {len(output_bytes)} bytes, base64 length: {len(output_b64)}")
                    
                    # Send processed audio and metrics back
                    emit('processed_audio', {
                        'audio': output_b64,
                        'metrics': {
                            'rms': float(rms),
                            'snr': float(snr),
                            'vad_confidence': float(vad_conf),
                            'pitch': float(pitch)
                        },
                        'status': 'processed'
                    })
                else:
                    emit('processed_audio', {
                        'metrics': {
                            'pitch': float(pitch)
                        },
                        'status': 'wrong_speaker'
                    })
            except Exception as processing_error:
                print(f"Audio processing error: {processing_error}")
                # Send error response
                emit('processed_audio', {
                    'status': 'error',
                    'message': str(processing_error)
                })
        else:
            emit('processed_audio', {'status': 'silence'})
            
    except Exception as e:
        print(f"Error processing audio: {e}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)