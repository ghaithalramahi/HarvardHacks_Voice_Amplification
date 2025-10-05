#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  4 16:12:26 2025

@author: ayskagadhwala
"""

import numpy as np


class AudioMetrics:
    """Calculate audio quality metrics."""
    
    @staticmethod
    def rms_energy(audio):
        """Root Mean Square energy (loudness)."""
        if audio.ndim == 2:
            audio = audio[:, 0]
        return np.sqrt(np.mean(audio**2))
    
    @staticmethod
    def snr(clean, noisy):
        """
        Signal-to-Noise Ratio in dB.
        clean: denoised audio
        noisy: original audio
        """
        if clean.ndim == 2:
            clean = clean[:, 0]
        if noisy.ndim == 2:
            noisy = noisy[:, 0]
        
        # Calculate noise as difference
        noise = noisy - clean
        
        signal_power = np.mean(clean**2)
        noise_power = np.mean(noise**2)
        
        if noise_power < 1e-10:
            return 100.0  # Very high SNR
        
        snr_value = 10 * np.log10(signal_power / noise_power)
        return snr_value
    
    @staticmethod
    def vad_confidence(audio, vad, is_speech):
        """
        VAD confidence score (0-1).
        Higher when audio is clearly speech or clearly silence.
        """
        if audio.ndim == 2:
            audio = audio[:, 0]
        
        # Energy-based confidence
        energy = np.max(np.abs(audio))
        
        if is_speech:
            # If speech detected, confidence is proportional to energy
            confidence = min(energy / 0.3, 1.0)
        else:
            # If silence detected, confidence is inverse of energy
            confidence = max(1.0 - (energy / 0.1), 0.0)
        
        return confidence