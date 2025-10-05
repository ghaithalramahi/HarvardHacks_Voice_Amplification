import sounddevice as sd
import numpy as np
from dsp.vad import VAD
from dsp.amplify import apply_gain
from dsp.denoiser import Denoiser
from dsp.speaker_filter import SpeakerFilter
from dsp.tone import confident_voice
from dsp.metrics import AudioMetrics


def main():
    # Initialize components
    print("Initializing components...")
    vad = VAD(mode=0)  # Most sensitive (good for whispers)
    denoiser = Denoiser()  # Facebook Denoiser
    speaker_filter = SpeakerFilter(target_pitch_range=(100, 250))  # Adjust for your voice
    metrics = AudioMetrics()
    
    gain = 8.0  # Amplification factor
    samplerate = 16000
    frame_len = vad.frame_len

    print("\n" + "="*60)
    print("🎤 Whisper Amplifier with Real-Time Metrics")
    print("="*60)
    print("\nSpeak into the mic - your whisper will be processed and amplified.")
    print("Press Ctrl+C to stop.\n")
    
    with sd.Stream(channels=1, samplerate=samplerate, dtype="float32") as stream:
        while True:
            # Read one frame
            input_audio, _ = stream.read(frame_len)
            frame = vad.float_to_bytes(input_audio[:, 0])

            # Check if speech is detected
            is_speech = vad.is_speech(frame) and np.max(np.abs(input_audio)) > 0.02
            
            if is_speech:
                # Check if it's the target speaker
                is_target, pitch = speaker_filter.is_target_speaker(input_audio)
                
                if is_target:
                    # Process audio
                    denoised = denoiser.process(input_audio)
                    enhanced = confident_voice(denoised, samplerate)
                    amplified = apply_gain(enhanced, gain)
                    
                    # Calculate metrics
                    rms = metrics.rms_energy(amplified)
                    snr = metrics.snr(denoised, input_audio)
                    vad_conf = metrics.vad_confidence(input_audio, vad, is_speech)
                    
                    # Output audio
                    stream.write(amplified)
                    
                    # Print metrics
                    print(f"✓ RMS: {rms:.4f} | SNR: {snr:.1f}dB | VAD: {vad_conf:.2f} | Pitch: {pitch:.0f}Hz")
                else:
                    # Wrong speaker - silence output
                    stream.write(np.zeros_like(input_audio))
                    print(f"✗ Wrong speaker (Pitch: {pitch:.0f}Hz) - filtered out")
            else:
                # Silence
                stream.write(np.zeros_like(input_audio))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
