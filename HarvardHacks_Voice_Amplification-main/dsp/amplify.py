#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  4 16:10:45 2025

@author: ayskagadhwala
"""

import numpy as np


def apply_gain(audio, gain):
    """
    Apply gain to denoised audio with intelligent processing.
    
    Args:
        audio: numpy array from denoiser output (float32, range -1 to 1)
        gain: gain factor (typically 1.5 to 3.0)
    
    Returns:
        amplified audio with proper dynamic range
    """
    # Handle different audio shapes
    original_shape = audio.shape
    if audio.ndim == 2:
        audio = audio[:, 0]  # Convert to 1D
    
    # Calculate RMS energy for dynamic gain adjustment
    rms = np.sqrt(np.mean(audio**2))
    
    # Maximum aggressive adaptive gain based on signal strength
    if rms > 0.1:  # Strong signal
        adaptive_gain = min(gain, 8.0)  # Allow very high gain for strong signals
    elif rms > 0.05:  # Medium signal
        adaptive_gain = gain * 1.5  # Increase medium signal gain
    else:  # Weak signal
        adaptive_gain = min(gain * 4.0, 20.0)  # Boost weak signals extremely
    
    # Apply adaptive gain
    amplified = audio * adaptive_gain
    
    # Lighter soft clipping to allow more amplification
    amplified = np.tanh(amplified * 0.7) * 1.3
    
    # Final clipping to ensure valid range
    amplified = np.clip(amplified, -1.0, 1.0)
    
    # Restore original shape
    if len(original_shape) == 2:
        amplified = amplified.reshape(-1, 1)
    
    return amplified


def apply_simple_gain(audio, gain):
    """Simple gain application (original function)."""
    amplified = audio * gain
    return np.clip(amplified, -1.0, 1.0)