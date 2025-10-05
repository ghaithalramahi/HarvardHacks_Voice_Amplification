import webrtcvad
import sounddevice as sd
import numpy as np


class VAD:
    """Voice Activity Detector with optional live microphone test."""
    
    def __init__(self, mode=2, samplerate=16000, frame_ms=30):
        """
        mode: 0–3 (0 = most sensitive, 3 = strict)
        samplerate: 8000, 16000, 32000, or 48000
        frame_ms: must be 10, 20, or 30
        """
        self.vad = webrtcvad.Vad(mode)
        self.samplerate = samplerate
        self.frame_ms = frame_ms
        self.frame_len = int(samplerate * frame_ms / 1000)
    
    def is_speech(self, frame_bytes):
        """Return True if this frame contains speech."""
        return self.vad.is_speech(frame_bytes, self.samplerate)
    
    def float_to_bytes(self, audio):
        """Convert float32 [-1,1] numpy array to 16-bit PCM bytes."""
        if audio.ndim == 2:
            audio = audio[:, 0]
        return (audio * 32767).astype(np.int16).tobytes()
    
    def listen_live(self):
        """Open the mic and print 'Speech' / 'Silence' in real time."""
        print("Speak to test VAD (Ctrl+C to quit)")
        with sd.InputStream(
            channels=1,
            samplerate=self.samplerate,
            blocksize=self.frame_len,
            dtype="float32",
        ) as stream:
            print("Microphone stream opened")
            while True:
                audio, overflowed = stream.read(self.frame_len)
                if overflowed:
                    print("Overflow:", overflowed)
                frame = self.float_to_bytes(audio[:, 0])
                if self.is_speech(frame) and np.max(np.abs(audio)) > 0.02:
                    print("Speech")
                else:
                    print("Silence")


# --- Run for quick test ---
if __name__ == "__main__":
    vad = VAD(mode=3)
    vad.listen_live()
