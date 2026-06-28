import cv2

def preprocess_image(image_path: str, dbg=None):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read image")

    # downscale image if it is too large to ensure consistent processing speed and accuracy
    max_dimension = 1000
    height, width = img.shape[:2]
    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        img = cv2.resize(img, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)


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

    if dbg:
        dbg.save(img, "01_original.png")
        dbg.save(gray, "02_gray.png")
        dbg.save(blurred, "03_blurred.png")
        dbg.save(cleaned, "04_binary.png")
        
    return gray, cleaned
