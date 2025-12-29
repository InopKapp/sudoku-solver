import cv2
import sys
import os

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read image")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    thresh = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    inverted = cv2.bitwise_not(thresh)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opened = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, kernel)

    cleaned = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)

    return img, gray, blurred, cleaned


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python preprocess.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    original, gray, blurred, cleaned = preprocess_image(image_path)

    os.makedirs("debug", exist_ok=True)

    cv2.imwrite("debug/1_original.png", original)
    cv2.imwrite("debug/2_gray.png", gray)
    cv2.imwrite("debug/3_blurred.png", blurred)
    cv2.imwrite("debug/4_preprocessed.png", cleaned)

    print("Preprocessing complete.")
    print("Check the images inside the 'debug/' folder.")
