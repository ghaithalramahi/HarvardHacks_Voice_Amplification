#!/usr/bin/env python3
"""
Test script to verify the voice amplification setup
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import numpy as np
        print("+ numpy")
    except ImportError as e:
        print(f"- numpy: {e}")
        return False
    
    try:
        import sounddevice as sd
        print("+ sounddevice")
    except ImportError as e:
        print(f"- sounddevice: {e}")
        return False
    
    try:
        import webrtcvad
        print("+ webrtcvad")
    except ImportError as e:
        print(f"- webrtcvad: {e}")
        return False
    
    try:
        import scipy
        print("+ scipy")
    except ImportError as e:
        print(f"- scipy: {e}")
        return False
    
    try:
        import torch
        print("+ torch")
    except ImportError as e:
        print(f"- torch: {e}")
        return False
    
    try:
        import flask
        print("+ flask")
    except ImportError as e:
        print(f"- flask: {e}")
        return False
    
    try:
        import flask_socketio
        print("+ flask-socketio")
    except ImportError as e:
        print(f"- flask-socketio: {e}")
        return False
    
    return True

def test_dsp_modules():
    """Test DSP modules"""
    print("\nTesting DSP modules...")
    
    try:
        from dsp.vad import VAD
        vad = VAD(mode=0, samplerate=16000)
        print("+ VAD")
    except Exception as e:
        print(f"- VAD: {e}")
        return False
    
    try:
        from dsp.denoiser import Denoiser
        denoiser = Denoiser(model_name="dns64", device="cpu")
        if denoiser.use_fallback:
            print("+ Denoiser (fallback mode)")
        else:
            print("+ Denoiser (Facebook model)")
    except Exception as e:
        print(f"- Denoiser: {e}")
        return False
    
    try:
        from dsp.speaker_filter import SpeakerFilter
        speaker_filter = SpeakerFilter(target_pitch_range=(100, 250), samplerate=16000)
        print("+ SpeakerFilter")
    except Exception as e:
        print(f"- SpeakerFilter: {e}")
        return False
    
    try:
        from dsp.amplify import apply_gain
        print("+ Amplify")
    except Exception as e:
        print(f"- Amplify: {e}")
        return False
    
    try:
        from dsp.tone import confident_voice
        print("+ Tone")
    except Exception as e:
        print(f"- Tone: {e}")
        return False
    
    try:
        from dsp.metrics import AudioMetrics
        print("+ Metrics")
    except Exception as e:
        print(f"- Metrics: {e}")
        return False
    
    return True

def test_server():
    """Test if server can start"""
    print("\nTesting server...")
    
    try:
        from server import app, socketio
        print("+ Server imports")
        return True
    except Exception as e:
        print(f"- Server: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Voice Amplification Setup Test")
    print("=" * 50)
    
    imports_ok = test_imports()
    dsp_ok = test_dsp_modules()
    server_ok = test_server()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Imports: {'+' if imports_ok else '-'}")
    print(f"DSP Modules: {'+' if dsp_ok else '-'}")
    print(f"Server: {'+' if server_ok else '-'}")
    
    if imports_ok and dsp_ok and server_ok:
        print("\n[SUCCESS] All tests passed! The setup should work.")
    else:
        print("\n[WARNING] Some tests failed. Check the errors above.")
    print("=" * 50)
