import numpy as np
import librosa
import scipy.signal as sp


def confident_voice(audio, sr):
    # 1️⃣ Denoise (optional if RNNoise already used)
    audio = librosa.effects.preemphasis(audio)

    # 2️⃣ Add subtle low–mid EQ boost (fuller voice)
    b, a = sp.butter(2, [100 / (sr / 2), 800 / (sr / 2)], btype="band")
    low_mid = sp.lfilter(b, a, audio)
    audio = audio + 0.4 * low_mid

    # 3️⃣ Light compression (steady loudness)
    audio = np.tanh(audio * 2.5)

    # 4️⃣ Slight high boost for clarity
    b, a = sp.butter(1, [3000 / (sr / 2)], btype="high")
    highs = sp.lfilter(b, a, audio)
    audio = audio + 0.2 * highs

    # 5️⃣ Add micro reverb (room presence)
    reverb = np.convolve(audio, np.ones(400) / 400, mode="full")[: len(audio)]
    audio = 0.7 * audio + 0.3 * reverb

    # Normalize
    audio = audio / np.max(np.abs(audio) + 1e-6)

    return audio.astype(np.float32)


# Parameters
samplerate = 16000
duration = 10

# 1️⃣ Record
print("🎤 Record your whisper...")
audio = sd.rec(
    int(duration * samplerate), samplerate=samplerate, channels=1, dtype="float32"
)
sd.wait()

# 2️⃣ Flatten & process
audio = audio[:, 0]
processed = confident_voice(audio, samplerate)

# 3️⃣ Playback
print("🔊 Playing processed 'confident' voice...")
sd.play(processed, samplerate)
sd.wait()
