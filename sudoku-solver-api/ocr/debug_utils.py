import os
import cv2

class OCRDebug:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        self.base_dir = "debug/ocr"

        if self.enabled:
            os.makedirs(self.base_dir, exist_ok=True)

    def save(self, img, relative_path):
        if not self.enabled:
            return

        full_path = os.path.join(self.base_dir, relative_path)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        cv2.imwrite(full_path, img)

    def log(self, msg):
        if self.enabled:
            print("[OCR DEBUG]", msg)
