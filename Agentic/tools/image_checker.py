import os
from PIL import Image
try:
    import pytesseract
    pytesseract_available = True
except ImportError:
    pytesseract_available = False

from google import genai
from google.genai import types

def simple_blur_detection(image: Image.Image, threshold=100) -> bool:
    try:
        import cv2
        import numpy as np
    except ImportError:
        # If cv2 or numpy missing, skip blur detection
        return True

    # Convert PIL Image to OpenCV Image
    open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance > threshold

def extract_text_from_image(image_path: str) -> str:
    if pytesseract_available:
        try:
            text = pytesseract.image_to_string(Image.open(image_path)).strip()
            return text
        except Exception:
            return ""
    else:
        # Fallback dummy text if pytesseract unavailable
        return ""

def image_quality_checks(image_path: str) -> str:
    try:
        image = Image.open(image_path)
    except Exception as e:
        return f"FAIL: Could not open image: {e}"

    # Example blur detection
    sharp_enough = simple_blur_detection(image)
    if not sharp_enough:
        return "FAIL: Image appears too blurry"

    return "PASS"

def image_checker(image_path: str, narrative: str = "", allow_text: bool = True) -> str:
    """
    Checks image quality and optionally detects unwanted text.
    - allow_text=True means text in image is allowed (e.g., flyer headline)
    - allow_text=False means image must be purely visual
    """
    print("Is pytesseract available? -->", pytesseract_available)

    # Step 1: Check image quality
    quality_result = image_quality_checks(image_path)
    if quality_result != "PASS":
        print("Fail due to quality")
        return quality_result

    # Step 2: Extract text from image
    extracted_text = extract_text_from_image(image_path)
    if extracted_text and not allow_text:
        print("Text found in the image")
        return "FAIL: No text must exist in the image"

    return "PASS"

# Example usage:
# result = image_checker("output/generated_image.png", "Promote green city initiative", allow_text=True)
# print(result)
