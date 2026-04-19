import cv2
import numpy as np

class HomomorphicFilter:
    def __init__(self, gl=0.5, gh=2.0, d0=30, c=1):
        self.gl = gl
        self.gh = gh
        self.d0 = d0
        self.c = c

    def __process_channel(self, channel):
        # 1. Log Transform [cite: 18, 27]
        img_log = np.log1p(np.array(channel, dtype="float"))
        
        # 2. FFT [cite: 20, 28]
        img_fft = np.fft.fft2(img_log)
        img_fft_shift = np.fft.fftshift(img_fft)
        
        # 3. High-Pass Filter Mask [cite: 12, 21, 29]
        rows, cols = channel.shape
        crow, ccol = rows // 2, cols // 2
        y, x = np.ogrid[-crow:rows-crow, -ccol:cols-ccol]
        dist_sq = x*x + y*y
        h_mask = (self.gh - self.gl) * (1 - np.exp(-self.c * (dist_sq / (self.d0**2)))) + self.gl
        
        # 4. Apply & Inverse [cite: 22, 30]
        filtered = img_fft_shift * h_mask
        img_ifft = np.fft.ifftshift(filtered)
        img_back = np.fft.ifft2(img_ifft)
        
        # 5. Exp & Normalize
        img_exp = np.expm1(np.real(img_back))
        return np.uint8(cv2.normalize(img_exp, None, 0, 255, cv2.NORM_MINMAX))

    def enhance(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            return None

        # Convert to HSV (Hue, Saturation, Value) [cite: 17, 26]
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # 1. Enhance Brightness (V) using Homomorphic Filtering 
        enhanced_v = self.__process_channel(v)
        
        # 2. Boost Saturation (S) to bring back colors [cite: 11, 23, 34]
        # We increase saturation because low-light images look "washed out"
        s = cv2.convertScaleAbs(s, alpha=1.2, beta=10) 
        
        # 3. Final Contrast Enhancement on V [cite: 23, 31]
        enhanced_v = cv2.equalizeHist(enhanced_v)
        
        # Merge and convert back to BGR [cite: 23, 32, 38]
        result_hsv = cv2.merge((h, s, enhanced_v))
        enhanced_bgr = cv2.cvtColor(result_hsv, cv2.COLOR_HSV2BGR)
        
        # 4. Denoise to clean up the grain from low-light [cite: 35]
        return cv2.fastNlMeansDenoisingColored(enhanced_bgr, None, 10, 10, 7, 21)

# Test it
if __name__ == "__main__":
    # Lower gl and moderate gh often look better for real color photos
    hf = HomomorphicFilter(gl=0.5, gh=1.5, d0=40) 
    result = hf.enhance('79.png')
    if result is not None:
        cv2.imwrite('enhanced_color_79.jpg', result)