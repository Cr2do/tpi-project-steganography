"""
Comparison metrics for steganography algorithms:
  - Invisibility  → PSNR  (Peak Signal-to-Noise Ratio, dB)
  - Capacity      → bpp   (bits per pixel)
  - Robustness    → BER   (Bit Error Rate) after various attacks
"""

import io
import numpy as np
from PIL import Image, ImageFilter


# ------------------------------------------------------------------ PSNR

def psnr(original: Image.Image, stego: Image.Image) -> float:
    """
    Compute PSNR between original and stego image.
    Higher is better (>40 dB = imperceptible, <30 dB = noticeable).
    """
    orig = np.array(original.convert("L"), dtype=np.float64)
    steg = np.array(stego.convert("L"), dtype=np.float64)
    mse = np.mean((orig - steg) ** 2)
    if mse == 0:
        return float("inf")
    return 10 * np.log10(255**2 / mse)


# ------------------------------------------------------------------ Capacity

def capacity_bpp(image: Image.Image, message_bits: int) -> float:
    """
    Compute the effective embedding rate in bits per pixel (bpp).
    """
    total_pixels = image.width * image.height
    return message_bits / total_pixels


# ------------------------------------------------------------------ BER

def ber(original_bits: list[int], recovered_bits: list[int]) -> float:
    """
    Bit Error Rate — fraction of bits recovered incorrectly.
    0.0 = perfect recovery, 0.5 = random noise.
    """
    length = min(len(original_bits), len(recovered_bits))
    if length == 0:
        return 0.0
    errors = sum(a != b for a, b in zip(original_bits[:length], recovered_bits[:length]))
    return errors / length


# ------------------------------------------------------------------ Robustness attacks

def attack_jpeg_compression(image: Image.Image, quality: int = 75) -> Image.Image:
    """Simulate JPEG compression/recompression."""
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    return Image.open(buf).copy()


def attack_gaussian_noise(image: Image.Image, std: float = 5.0) -> Image.Image:
    """Add Gaussian noise (simulate re-recording / analog noise)."""
    arr = np.array(image, dtype=np.float64)
    noise = np.random.normal(0, std, arr.shape)
    noisy = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy, image.mode)


def attack_crop(image: Image.Image, crop_fraction: float = 0.1) -> Image.Image:
    """Crop a fraction of the image border, then resize back to original."""
    w, h = image.size
    margin_x = int(w * crop_fraction)
    margin_y = int(h * crop_fraction)
    cropped = image.crop((margin_x, margin_y, w - margin_x, h - margin_y))
    return cropped.resize((w, h), Image.LANCZOS)


def attack_rotation(image: Image.Image, angle: float = 5.0) -> Image.Image:
    """Rotate by a small angle and restore size."""
    return image.rotate(angle, resample=Image.BICUBIC, expand=False)


def attack_blur(image: Image.Image, radius: float = 1.5) -> Image.Image:
    """Apply Gaussian blur."""
    return image.filter(ImageFilter.GaussianBlur(radius=radius))


# ------------------------------------------------------------------ Full robustness report

ATTACKS = {
    "jpeg_q75": lambda img: attack_jpeg_compression(img, quality=75),
    "jpeg_q50": lambda img: attack_jpeg_compression(img, quality=50),
    "gaussian_noise": lambda img: attack_gaussian_noise(img, std=5.0),
    "crop_10pct": lambda img: attack_crop(img, crop_fraction=0.10),
    "rotation_5deg": lambda img: attack_rotation(img, angle=5.0),
    "blur": lambda img: attack_blur(img, radius=1.5),
}


def robustness_report(
    stego: Image.Image,
    original_bits: list[int],
    extract_fn,  # callable(attacked_image) -> bytes
) -> dict[str, float]:
    """
    Run all attacks and return a dict of {attack_name: BER}.
    extract_fn should extract and return bytes from the attacked image.
    """
    report = {}
    for name, attack in ATTACKS.items():
        try:
            attacked = attack(stego)
            recovered = extract_fn(attacked)
            recovered_bits = [int(b) for byte in recovered for b in f"{byte:08b}"]
            report[name] = ber(original_bits, recovered_bits)
        except Exception as exc:
            report[name] = f"error: {exc}"
    return report
