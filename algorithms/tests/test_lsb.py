"""
Tests for the LSB steganography algorithm.
Covers: correctness, capacity, invisibility (PSNR), robustness (BER).
"""

import numpy as np
import pytest
from PIL import Image

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lsb import LSB
from src.metrics import psnr, capacity_bpp, ber, robustness_report


# ------------------------------------------------------------------ correctness

def test_embed_extract_roundtrip(rgb_image, medium_message):
    algo = LSB()
    stego = algo.embed(rgb_image, medium_message)
    assert algo.extract(stego) == medium_message


def test_embed_extract_short_message(rgb_image, short_message):
    algo = LSB()
    stego = algo.embed(rgb_image, short_message)
    assert algo.extract(stego) == short_message


def test_embed_extract_binary_message(rgb_image):
    algo = LSB()
    msg = bytes(range(256))  # all byte values
    stego = algo.embed(rgb_image, msg)
    assert algo.extract(stego) == msg


def test_message_too_large_raises(gray_image):
    algo = LSB()
    # 128x128 grayscale = 16384 channels → can hold 16384/8 - delimiter = ~2045 bytes
    huge_msg = b"A" * 3000
    with pytest.raises(ValueError, match="too large"):
        algo.embed(gray_image, huge_msg)


def test_extract_without_embed_raises(rgb_image):
    algo = LSB()
    with pytest.raises(ValueError, match="Delimiter not found"):
        algo.extract(rgb_image)


# ------------------------------------------------------------------ invisibility (PSNR)

def test_psnr_above_40db(rgb_image, medium_message):
    """LSB should be imperceptible: PSNR > 40 dB."""
    algo = LSB()
    stego = algo.embed(rgb_image, medium_message)
    score = psnr(rgb_image, stego)
    print(f"\n[LSB] PSNR = {score:.2f} dB")
    assert score > 40.0


# ------------------------------------------------------------------ capacity (bpp)

def test_capacity_bpp(rgb_image, medium_message):
    bpp = capacity_bpp(rgb_image, len(medium_message) * 8)
    print(f"\n[LSB] bpp = {bpp:.4f}")
    # LSB on RGB: theoretical max = 3 bpp (1 bit per channel)
    assert bpp > 0


def test_max_capacity(rgb_image):
    """Embed the maximum possible message without error."""
    algo = LSB()
    w, h = rgb_image.size
    channels = w * h * 3  # RGB
    max_bytes = channels // 8 - len(algo.DELIMITER) - 1
    msg = b"X" * max_bytes
    stego = algo.embed(rgb_image, msg)
    assert algo.extract(stego) == msg


# ------------------------------------------------------------------ robustness (BER)

def test_robustness_report(rgb_image, medium_message, medium_message_bits):
    algo = LSB()
    stego = algo.embed(rgb_image, medium_message)

    def extract_fn(attacked_img):
        try:
            return algo.extract(attacked_img)
        except ValueError:
            return b""

    report = robustness_report(stego, medium_message_bits, extract_fn)
    print("\n[LSB] Robustness report:")
    for attack, score in report.items():
        print(f"  {attack}: BER = {score}")

    # LSB survives no-op but breaks under JPEG / noise — BER should be 0 on lossless attacks
    # We just verify the report runs without crashing
    assert "jpeg_q75" in report
    assert "gaussian_noise" in report
