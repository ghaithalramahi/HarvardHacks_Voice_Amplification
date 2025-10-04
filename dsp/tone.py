import sounddevice as sd
import numpy as np
from dsp.vad import VAD
from dsp.denoiser import Denoiser
from tone import confident_voice  # your tonal enhancer


def main():
    vad = VAD(mode=0)  # Sensitive to whispers
    denoiser = Denoiser()
    samplerate = 16000
    frame_len = vad.frame_len

    print("Whisper into the mic — your voice will be denoised and made confident.")
    with sd.Stream(channels=1, samplerate=samplerate, dtype="float32") as stream:
        while True:
            # 1️⃣ Capture one frame
            input_audio, _ = stream.read(frame_len)
            frame = vad.float_to_bytes(input_audio[:, 0])

            # 2️⃣ Process only if speech detected
            if vad.is_speech(frame) and np.max(np.abs(input_audio)) > 0.02:
                # Denoise
                denoised = denoiser.process(input_audio)

                # Apply tonal shaping (confidence effect)
                confident = confident_voice(denoised[:, 0], samplerate)
                confident = confident.reshape(-1, 1)

                # Play processed frame
                stream.write(confident)
                print("Confident whisper detected — enhanced output.")
            else:
                # Write silence
                stream.write(np.zeros_like(input_audio))
