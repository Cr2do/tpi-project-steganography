"""
Unit tests for the metrics module (PSNR, bpp, BER, attacks).
"""

import numpy as np
import pytest
from PIL import Image

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.metrics import (
    psnr,
    capacity_bpp,
    ber,
    attack_jpeg_compression,
    attack_gaussian_noise,
    attack_crop,
    attack_rotation,
    attack_blur,
)


# ------------------------------------------------------------------ PSNR

def test_psnr_identical_images(rgb_image):
    assert psnr(rgb_image, rgb_image) == float("inf")


def test_psnr_completely_different(rgb_image):
    black = Image.fromarray(np.zeros((128, 128, 3), dtype=np.uint8), "RGB")
    score = psnr(rgb_image, black)
    assert score < 20.0


def test_psnr_range(rgb_image):
    noisy_arr = np.clip(np.array(rgb_image, dtype=np.float64) + 5, 0, 255).astype(np.uint8)
    noisy = Image.fromarray(noisy_arr, "RGB")
    score = psnr(rgb_image, noisy)
    assert 30.0 < score < 60.0


# ------------------------------------------------------------------ BER

def test_ber_perfect():
    bits = [1, 0, 1, 1, 0]
    assert ber(bits, bits) == 0.0


def test_ber_all_wrong():
    original = [1, 1, 1, 1]
    recovered = [0, 0, 0, 0]
    assert ber(original, recovered) == 1.0


def test_ber_half_wrong():
    original = [1, 0, 1, 0]
    recovered = [0, 1, 1, 0]
    assert ber(original, recovered) == 0.5


def test_ber_different_lengths():
    # Should compare only up to shortest length
    original = [1, 0, 1, 0, 1]
    recovered = [1, 0, 1]
    assert ber(original, recovered) == 0.0


def test_ber_empty():
    assert ber([], []) == 0.0


# ------------------------------------------------------------------ capacity bpp

def test_bpp_calculation(rgb_image):
    bits = 128 * 128 * 1  # 1 bit per pixel
    result = capacity_bpp(rgb_image, bits)
    assert result == pytest.approx(1.0)


def test_bpp_small_message(rgb_image):
    result = capacity_bpp(rgb_image, 8)  # 1 byte in a 128x128 image
    assert result == pytest.approx(8 / (128 * 128))


# ------------------------------------------------------------------ attacks

def test_jpeg_attack_changes_image(rgb_image):
    attacked = attack_jpeg_compression(rgb_image, quality=50)
    assert np.any(np.array(rgb_image) != np.array(attacked.convert("RGB")))


def test_jpeg_attack_preserves_size(rgb_image):
    attacked = attack_jpeg_compression(rgb_image)
    assert attacked.size == rgb_image.size


def test_noise_attack_changes_image(rgb_image):
    attacked = attack_gaussian_noise(rgb_image, std=10.0)
    assert np.any(np.array(rgb_image) != np.array(attacked))


def test_crop_attack_preserves_size(rgb_image):
    attacked = attack_crop(rgb_image, crop_fraction=0.1)
    assert attacked.size == rgb_image.size


def test_rotation_attack_preserves_size(rgb_image):
    attacked = attack_rotation(rgb_image, angle=10.0)
    assert attacked.size == rgb_image.size


def test_blur_attack_changes_image(rgb_image):
    attacked = attack_blur(rgb_image, radius=2.0)
    assert np.any(np.array(rgb_image) != np.array(attacked))
