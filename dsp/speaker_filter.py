#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  4 16:12:06 2025
@author: ayskagadhwala
"""
import numpy as np
from scipy.fft import rfft, rfftfreq


class SpeakerFilter:
    """Simple speaker recognition based on pitch range."""
    
    def __init__(self, target_pitch_range=(100, 250), samplerate=16000):
        """
        target_pitch_range: (min_hz, max_hz) - typical male 85-180, female 165-255
        """
        self.min_pitch = target_pitch_range[0]
        self.max_pitch = target_pitch_range[1]
        self.sr = samplerate
        
    def is_target_speaker(self, audio):
        """
        Check if audio matches target speaker's pitch range.
        Returns: (is_match: bool, dominant_pitch: float)
        """
        if audio.ndim == 2:
            audio = audio[:, 0]
        
        # Skip if too quiet
        if np.max(np.abs(audio)) < 0.02:
            return False, 0.0
        
        # Get dominant frequency using FFT
        fft = np.abs(rfft(audio))
        freqs = rfftfreq(len(audio), 1/self.sr)
        
        # Find peak in speech range (80-400 Hz)
        speech_mask = (freqs >= 80) & (freqs <= 400)
        if not np.any(speech_mask):
            return False, 0.0
        
        peak_idx = np.argmax(fft[speech_mask])
        dominant_pitch = freqs[speech_mask][peak_idx]
        
        # Check if in target range
        is_match = self.min_pitch <= dominant_pitch <= self.max_pitch
        
        return is_match, dominant_pitch
