import sounddevice as sd
import numpy as np
from dsp.vad import VAD
from dsp.amplify import apply_gain
from dsp.denoiser import Denoiser
from dsp.speaker_filter import SpeakerFilter
from dsp.tone import confident_voice
from dsp.metrics import AudioMetrics

def main():
    vad = VAD(mode=0)
    denoiser = Denoiser()
    speaker_filter = SpeakerFilter(target_pitch_range=(100, 250))
    metrics = AudioMetrics()

    gain = 8.0
    samplerate = 16000
    frame_len = vad.frame_len

    print("\n" + "="*60)
    print("🎤 SpeakNow")
    print("="*60)
    print("\nSpeak into the mic - your whisper will be processed and amplified.")
    print("Press Ctrl+C to stop.\n")

    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)
        input_audio = indata.copy()

        frame = vad.float_to_bytes(input_audio[:, 0])
        is_speech = vad.is_speech(frame) and np.max(np.abs(input_audio)) > 0.02

        if is_speech:
            is_target, pitch = speaker_filter.is_target_speaker(input_audio)
            if is_target:
                denoised = denoiser.process(input_audio)
                enhanced = confident_voice(denoised, samplerate)
                amplified = apply_gain(enhanced, gain)

                rms = metrics.rms_energy(amplified)
                snr = metrics.snr(denoised, input_audio)
                vad_conf = metrics.vad_confidence(input_audio, vad, is_speech)

                outdata[:] = amplified
                print(f"✓ RMS: {rms:.4f} | SNR: {snr:.1f}dB | VAD: {vad_conf:.2f} | Pitch: {pitch:.0f}Hz")
            else:
                outdata[:] = 0
                print(f"✗ Wrong speaker (Pitch: {pitch:.0f}Hz) - filtered out")
        else:
            outdata[:] = 0

    with sd.Stream(channels=1, samplerate=samplerate, dtype="float32", callback=callback):
        sd.sleep(10000000)  # Run until interrupted

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
