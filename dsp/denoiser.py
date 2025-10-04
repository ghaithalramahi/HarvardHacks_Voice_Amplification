import torch
import sounddevice as sd
import numpy as np
from denoiser import pretrained
from vad import VAD  # your existing VAD class

# --------------------------
# Load Facebook Denoiser
# --------------------------
model = pretrained.dns64().eval()

# --------------------------
# Configuration
# --------------------------
SAMPLERATE = 16000
FRAME_MS = 30
FRAME_LEN = int(SAMPLERATE * FRAME_MS / 1000)

# --------------------------
# Initialize VAD
# --------------------------
vad = VAD(mode=3, samplerate=SAMPLERATE, frame_ms=FRAME_MS)

# --------------------------
# Audio callback for real-time denoising
# --------------------------
def audio_callback(indata, outdata, frames, time, status):
    if status:
        print(status)

    # Convert incoming audio to torch tensor
    audio_tensor = torch.tensor(indata, dtype=torch.float32).t()

    # Convert audio to 16-bit PCM bytes for VAD
    frame_bytes = vad.float_to_bytes(indata[:, 0])

    # Only denoise if VAD detects speech
    if vad.is_speech(frame_bytes) and np.max(np.abs(indata)) > 0.02:
        with torch.no_grad():
            clean = model(audio_tensor)
        outdata[:] = clean.t().numpy()
    else:
        # No speech detected → output original audio (or silence)
        outdata[:] = indata

# --------------------------
# Run real-time microphone stream
# --------------------------
if __name__ == "__main__":
    print(" Real-time denoiser running (Ctrl+C to stop)")
    with sd.Stream(
        samplerate=SAMPLERATE,
        blocksize=FRAME_LEN,
        dtype="float32",
        channels=1,
        callback=audio_callback,
    ):
        import time
        while True:
            time.sleep(1)
