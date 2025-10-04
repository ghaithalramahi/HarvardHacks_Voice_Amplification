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
gain = 8.0
samplerate = 16000

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global vad, denoiser, speaker_filter
    print('Client connected')
    
    # Initialize components on first connection
    if vad is None:
        print("Initializing audio processing pipeline...")
        vad = VAD(mode=0, samplerate=samplerate)
        denoiser = Denoiser(model_name="dns64", device="cpu")
        speaker_filter = SpeakerFilter(target_pitch_range=(100, 250), samplerate=samplerate)
        print("✓ Pipeline ready")
    
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
        
        # Check if speech detected
        frame_bytes = vad.float_to_bytes(audio)
        is_speech = vad.is_speech(frame_bytes) and np.max(np.abs(audio)) > 0.02
        
        if is_speech:
            # Check if target speaker
            is_target, pitch = speaker_filter.is_target_speaker(audio)
            
            if is_target:
                # Process audio
                denoised = denoiser.process(audio, sr=samplerate)
                enhanced = confident_voice(denoised, samplerate)
                amplified = apply_gain(enhanced, gain)
                
                # Calculate metrics
                rms = metrics.rms_energy(amplified)
                snr = metrics.snr(denoised, audio)
                vad_conf = metrics.vad_confidence(audio, vad, is_speech)
                
                # Convert back to bytes and base64
                output_bytes = (amplified * 32767).astype(np.int16).tobytes()
                output_b64 = base64.b64encode(output_bytes).decode('utf-8')
                
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
        else:
            emit('processed_audio', {'status': 'silence'})
            
    except Exception as e:
        print(f"Error processing audio: {e}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)