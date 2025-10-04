#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  4 16:10:45 2025

@author: ayskagadhwala
"""

import numpy as np


def apply_gain(audio, gain):
    """Apply gain and prevent clipping."""
    amplified = audio * gain
    return np.clip(amplified, -1.0, 1.0)