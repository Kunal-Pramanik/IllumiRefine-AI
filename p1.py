import cv2
import numpy as np

class HomomorphicFilter:
    def __init__(self, gl=0.4, gh=1.5, d0=40, c=1):
        self.gl = gl
        self.gh = gh
        self.d0 = d0
        self.c = c

    def __process_channel(self, channel):
        # 1. Log Transform to separate illumination and reflectance [cite: 18, 27]
        img_log = np.log1p(np.array(channel, dtype="float"))
        
        # 2. Fourier Transform to convert to frequency domain [cite: 20, 28]
        img_fft = np.fft.fft2(img_log)
        img_fft_shift = np.fft.fftshift(img_fft)
        
        # 3. Create High-Pass Filter Mask 
        rows, cols = channel.shape
        crow, ccol = rows // 2, cols // 2
        y, x = np.ogrid[-crow:rows-crow, -ccol:cols-ccol]
        dist_sq = x*x + y*y
        h_mask = (self.gh - self.gl) * (1 - np.exp(-self.c * (dist_sq / (self.d0**2)))) + self.gl
        
        # 4. Apply filter and perform Inverse Fourier Transform 
        filtered = img_fft_shift * h_mask
        img_ifft = np.fft.ifftshift(filtered)
        img_back = np.fft.ifft2(img_ifft)
        
        # 5. Inverse Log (Exponential) and Normalization
        img_exp = np.expm1(np.real(img_back))
        return np.uint8(cv2.normalize(img_exp, None, 0, 255, cv2.NORM_MINMAX))

    def enhance(self, image_path):
        img = cv2.imread(image_path)
        if img is None: 
            return None

        # 1. PRE-PROCESSING: Gentle Denoising [cite: 26]
        img = cv2.fastNlMeansDenoisingColored(img, None, 5, 5, 7, 21)

        # 2. ENHANCE: Homomorphic Processing via HSV [cite: 12, 14, 21]
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # Process ONLY the illumination/value channel [cite: 12, 14, 21]
        enhanced_v = self.__process_channel(v)
        
        # Gentle Saturation boost to restore colors
        s = cv2.convertScaleAbs(s, alpha=1.1, beta=5) 
        
        # 3. CONTRAST: Apply CLAHE for localized enhancement 
        clahe = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(8,8))
        enhanced_v = clahe.apply(enhanced_v)
        
        # Merge back to BGR
        enhanced_bgr = cv2.cvtColor(cv2.merge((h, s, enhanced_v)), cv2.COLOR_HSV2BGR)
        
        # 4. SHARPEN: Unsharp Masking to restore structural details
        gaussian_blur = cv2.GaussianBlur(enhanced_bgr, (5, 5), 1.0)
        sharpened = cv2.addWeighted(enhanced_bgr, 1.5, gaussian_blur, -0.5, 0)
        
        # 5. REFINEMENT: Bilateral Filter for edge-preserving smoothness
        return cv2.bilateralFilter(sharpened, 7, 50, 50)

if __name__ == "__main__":
    # Parameters set for low-light enhancement [cite: 14]
    hf = HomomorphicFilter(gl=0.5, gh=1.2, d0=30) 
    result = hf.enhance('79.png')
    if result is not None:
        cv2.imwrite('enhanced_79clean.jpg', result)