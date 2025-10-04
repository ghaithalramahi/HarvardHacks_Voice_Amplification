import sounddevice as sd
import numpy as np
from dsp.vad import VAD
from dsp.amplify import apply_gain
from dsp.denoiser import Denoiser


def main():
    # Initialize components
    vad = VAD(mode=0)  # Most sensitive (good for whispers)
    denoiser = Denoiser()  # Denoise
    gain = 8.0  # Amplification factor
    samplerate = 16000
    frame_len = vad.frame_len

    print("Whisper into the mic — your voice will be amplified and played back.")
    with sd.Stream(channels=1, samplerate=samplerate, dtype="float32") as stream:
        while True:
            # Read one frame
            input_audio, _ = stream.read(frame_len)
            frame = vad.float_to_bytes(input_audio[:, 0])

            # Check if speech is detected
            if vad.is_speech(frame) and np.max(np.abs(input_audio)) > 0.02:
                denoised = denoiser.process(input_audio)
                amplified = apply_gain(denoised, gain)
                stream.write(amplified)
                print("Whisper detected — amplified output.")
            else:
                stream.write(np.zeros_like(input_audio))
