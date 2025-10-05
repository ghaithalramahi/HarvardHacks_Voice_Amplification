#!/usr/bin/env python3
"""
Simple server for testing voice amplification
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import numpy as np
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug')
def debug():
    with open('debug_audio.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/test')
def test():
    with open('audio_test.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/output')
def output():
    with open('audio_output_test.html', 'r', encoding='utf-8') as f:
        return f.read()

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('ready', {'message': 'Server ready to process audio'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('test')
def handle_test(data):
    print(f'Test message received: {data}')
    emit('test_response', {'message': 'Server received your test message!'})

@socketio.on('audio_data')
def handle_audio(data):
    """Process incoming audio chunks from browser"""
    try:
        print("Received audio data")
        
        # Decode base64 audio data
        audio_bytes = base64.b64decode(data['audio'])
        
        # Convert bytes to numpy array (assuming float32 PCM)
        audio = np.frombuffer(audio_bytes, dtype=np.float32)
        
        # Debug: Print more details about the audio data
        print(f"Audio data size: {len(audio_bytes)} bytes, shape: {audio.shape}")
        print(f"Audio range: [{np.min(audio):.6f}, {np.max(audio):.6f}]")
        
        # Simple test - just echo back the audio level
        max_level = np.max(np.abs(audio))
        rms_level = np.sqrt(np.mean(audio**2))
        
        print(f"Max level: {max_level:.6f}, RMS: {rms_level:.6f}")
        
        # Send back a simple response
        emit('processed_audio', {
            'metrics': {
                'rms': float(max_level),
                'snr': 20.0,
                'vad_confidence': 0.8 if max_level > 0.01 else 0.0,
                'pitch': 150.0
            },
            'status': 'processed' if max_level > 0.01 else 'silence'
        })
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    print("Starting simple voice amplification server...")
    print("Open your browser to: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
