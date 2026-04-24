import hashlib
import cv2
import numpy as np


def decode_qr(image_bytes: bytes) -> str:
    """
    Decode QR code from raw image bytes.
    Raises ValueError if no QR is found.
    """

    # Convert bytes → numpy array
    np_arr = np.frombuffer(image_bytes, np.uint8)

    # Decode image
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Invalid image data")

    # Initialize QR detector
    detector = cv2.QRCodeDetector()

    # Detect & decode
    data, bbox, _ = detector.detectAndDecode(img)

    if not data:
        raise ValueError("No QR code detected in image")

    return data


def generate_fingerprint(qr_data: str) -> str:
    """
    SHA-256 fingerprint of QR data.
    Deterministic & collision-resistant.
    """
    return hashlib.sha256(qr_data.encode("utf-8")).hexdigest()