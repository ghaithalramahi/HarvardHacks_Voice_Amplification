import numpy as np
import librosa
import scipy.signal as sp


def confident_voice(audio, sr):
    """Apply tone enhancement for confident voice."""
    
    # Handle shape
    if audio.ndim == 2:
        audio = audio[:, 0]
    
    # 1️⃣ Preemphasis
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
    audio = audio / (np.max(np.abs(audio)) + 1e-6)

    return audio.astype(np.float32).reshape(-1, 1)
