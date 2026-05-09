import torch
import torch.nn as nn
import cv2
import numpy as np

# --- The Standard SCI Network Architecture ---
class EnhanceNetwork(nn.Module):
    def __init__(self, layers=1, channels=3):
        super(EnhanceNetwork, self).__init__()
        self.in_conv = nn.Sequential(
            nn.Conv2d(3, channels, kernel_size=3, stride=1, padding=1),
            nn.ReLU()
        )
        self.conv = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU()
        )
        self.blocks = nn.ModuleList([self.conv for _ in range(layers)])
        self.out_conv = nn.Sequential(
            nn.Conv2d(channels, 3, kernel_size=3, stride=1, padding=1),
            nn.Sigmoid()
        )

    def forward(self, input):
        fea = self.in_conv(input)
        for conv in self.blocks:
            fea = fea + conv(fea)
        fea = self.out_conv(fea)
        illum = fea + input 
        return illum

class SCIFilter:
    def __init__(self, weights_path='weights/difficult.pt'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = EnhanceNetwork(layers=1, channels=3).to(self.device)
        
        try:
            full_state_dict = torch.load(weights_path, map_location=self.device)
            enhance_dict = {k.replace('enhance.', ''): v for k, v in full_state_dict.items() if k.startswith('enhance.')}
            self.model.load_state_dict(enhance_dict)
            self.model.eval()
            print("✅ SCI Model loaded successfully!")
        except Exception as e:
            print(f"CRITICAL ERROR: {e}")

    def enhance(self, image_path):
        img = cv2.imread(image_path)
        if img is None: return None
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_normalized = (np.asarray(img_rgb) / 255.0).astype(np.float32)
        img_tensor = torch.from_numpy(img_normalized).permute(2, 0, 1).unsqueeze(0).to(self.device)

        with torch.no_grad():
            # 1. AI estimates the Illumination Map
            illumination_map = self.model(img_tensor)
            
            # 2. Standard Retinex Division
            enhanced_tensor = img_tensor / (illumination_map + 1e-4) 

            # --- NOVEL TWEAK 1: Exposure and Gamma Boost ---
            # Multiply by a gain > 1 to artificially boost global brightness
            exposure_gain = 1.8 
            enhanced_tensor = enhanced_tensor * exposure_gain
            
            # Apply fractional gamma (< 1) to lift the dark shadows further 
            # without blowing out the bright red clock
            post_gamma = 0.75 
            enhanced_tensor = torch.pow(enhanced_tensor, post_gamma)

            # Clamp to ensure no pixels overflow to pure white artifacts
            enhanced_tensor = torch.clamp(enhanced_tensor, 0, 1)

        # Convert tensors back to OpenCV NumPy format
        enhanced_bgr = cv2.cvtColor((enhanced_tensor.squeeze().permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
        illum_weight = illumination_map.squeeze().permute(1, 2, 0).cpu().numpy() # Shape: (H, W, 3), range 0-1

        # --- NOVEL TWEAK 2: Illumination-Guided Adaptive Denoising ---
        # 1. We apply a heavy Non-Local Means Denoiser to the whole image
        denoised_bgr = cv2.fastNlMeansDenoisingColored(enhanced_bgr, None, h=12, hColor=12, templateWindowSize=7, searchWindowSize=21)
        
        # 2. Smart Blending using the AI's Illumination Map
        # If a pixel was originally dark (illum_weight is near 0), (1 - illum_weight) is near 1 -> Use Denoised pixel
        # If a pixel was originally bright (illum_weight is near 1), (1 - illum_weight) is near 0 -> Use Sharp/Original pixel
        final_hybrid = (denoised_bgr * (1 - illum_weight)) + (enhanced_bgr * illum_weight)
        
        # Ensure values are valid 8-bit integers
        final_result = np.clip(final_hybrid, 0, 255).astype(np.uint8)

        return final_result
