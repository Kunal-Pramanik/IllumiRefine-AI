import torch
import torch.nn as nn
import cv2
import numpy as np

class EnhanceNetwork(nn.Module):
    def __init__(self, layers=1, channels=3):
        super(EnhanceNetwork, self).__init__()
        
        # 1. Input Convolution
        self.in_conv = nn.Sequential(
            nn.Conv2d(3, channels, kernel_size=3, stride=1, padding=1),
            nn.ReLU()
        )
        # 2. Main Processing Block (Matches the keys in your error)
        self.conv = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU()
        )
        self.blocks = nn.ModuleList()
        for i in range(layers):
            self.blocks.append(self.conv)
            
        # 3. Output Convolution
        self.out_conv = nn.Sequential(
            nn.Conv2d(channels, 3, kernel_size=3, stride=1, padding=1),
            nn.Sigmoid()
        )

    def forward(self, input):
        fea = self.in_conv(input)
        for conv in self.blocks:
            fea = fea + conv(fea)
        fea = self.out_conv(fea)
        # SCI estimates the residual, so Illumination = Residual + Input
        illum = fea + input 
        return illum

class SCIFilter:
    def __init__(self, weights_path='weights/difficult.pt'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = EnhanceNetwork(layers=1, channels=3).to(self.device)
        
        try:
            # 1. Load the full weights dictionary
            full_state_dict = torch.load(weights_path, map_location=self.device)
            
            # 2. Extract ONLY the 'enhance' network keys
            enhance_dict = {}
            for key, value in full_state_dict.items():
                if key.startswith('enhance.'):
                    # Remove the 'enhance.' prefix so it matches our class names
                    new_key = key.replace('enhance.', '')
                    enhance_dict[new_key] = value
                    
            # 3. Load the filtered weights into our model
            self.model.load_state_dict(enhance_dict)
            self.model.eval()
            print("✅ SCI Model loaded successfully!")
        except Exception as e:
            print(f"CRITICAL ERROR: {e}")

    def enhance(self, image_path):
        img = cv2.imread(image_path)
        if img is None: return None
        
        # Prepare image for PyTorch
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_normalized = (np.asarray(img) / 255.0).astype(np.float32)
        img_tensor = torch.from_numpy(img_normalized).permute(2, 0, 1).unsqueeze(0).to(self.device)

        # Run AI Inference
        with torch.no_grad():
            illumination_map = self.model(img_tensor)
            # Retinex formulation: Clear Image = Low Light / Illumination Map
            enhanced_tensor = img_tensor / (illumination_map + 1e-4) 
            enhanced_tensor = torch.clamp(enhanced_tensor, 0, 1)

        # Convert back to OpenCV BGR format
        enhanced_numpy = enhanced_tensor.squeeze().permute(1, 2, 0).cpu().numpy()
        enhanced_bgr = cv2.cvtColor((enhanced_numpy * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
        return enhanced_bgr