import sounddevice as sd
import numpy as np

def apply_gain(audio, gain):
    """Apply gain and prevent clipping."""
    amplified = audio * gain
    return np.clip(amplified, -1.0, 1.0)

def amplify_stream(gain=2.0):
    """Amplify microphone input and play in real time."""
    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)
        outdata[:] = apply_gain(indata, gain)

    with sd.Stream(callback=callback):
        print("🎙️ Real-time amplification started. Press Ctrl+C to stop.")
        sd.sleep(1000000)  # Keep running

if __name__ == "__main__":
    amplify_stream(gain=2.0)
