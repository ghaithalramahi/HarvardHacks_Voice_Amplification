import torch
import torchaudio
import numpy as np
import os
import sys

# Add Facebook denoiser path 

from denoiser import pretrained
from denoiser.dsp import convert_audio


class Denoiser:
    """Facebook Denoiser wrapper (from facebook/denoiser repo)."""
    
    def __init__(self, model_name="dns64", device="cpu"):
        """
        Initialize Facebook Denoiser.
        model_name: "dns48", "dns64", "master64" 
        device: "cpu" or "cuda"
        """
        print(f"Loading Facebook Denoiser model: {model_name}...")
        
        self.device = device
        self.model = pretrained.get_model(model_name).to(device)
        self.model.eval()
        
        # Model expects 16kHz
        self.model_sr = 16000
        print("✓ Denoiser loaded successfully")
        
    def process(self, audio, sr=16000):
        """
        Denoise audio chunk.
        audio: numpy array (frame_len, 1) or (frame_len,)
        sr: sample rate (will resample if needed)
        returns: denoised numpy array same shape as input
        """
        # Store original shape
        original_shape = audio.shape
        
        # Flatten if 2D
        if audio.ndim == 2:
            audio = audio[:, 0]
        
        # Convert to torch tensor (1, 1, samples) - batch, channels, samples
        audio_tensor = torch.from_numpy(audio).float().unsqueeze(0).unsqueeze(0)
        
        # Resample if needed
        if sr != self.model_sr:
            audio_tensor = convert_audio(
                audio_tensor, 
                sr, 
                self.model_sr, 
                self.model.chin
            )
        
        # Move to device
        audio_tensor = audio_tensor.to(self.device)
        
        # Denoise
        with torch.no_grad():
            denoised = self.model(audio_tensor)
        
        # Convert back to numpy
        denoised = denoised.squeeze().cpu().numpy()
        
        # Resample back if needed
        if sr != self.model_sr:
            denoised_tensor = torch.from_numpy(denoised).unsqueeze(0).unsqueeze(0)
            denoised_tensor = convert_audio(
                denoised_tensor,
                self.model_sr,
                sr,
                1
            )
            denoised = denoised_tensor.squeeze().cpu().numpy()
        
        # Reshape to match input
        if len(original_shape) == 2:
            denoised = denoised.reshape(-1, 1)
        
        return denoised



