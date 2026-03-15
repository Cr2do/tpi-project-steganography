"""
Tests for the DCT steganography algorithm.
Covers: correctness, capacity, invisibility (PSNR), robustness (BER).
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.dct import DCT
from src.metrics import psnr, capacity_bpp, ber, robustness_report


# ------------------------------------------------------------------ correctness

def test_embed_extract_roundtrip(gray_image, medium_message):
    algo = DCT()
    stego = algo.embed(gray_image, medium_message)
    assert algo.extract(stego) == medium_message


def test_embed_extract_rgb_image(rgb_image, medium_message):
    """DCT works on RGB images (converts to L internally)."""
    algo = DCT()
    stego = algo.embed(rgb_image, medium_message)
    assert algo.extract(stego) == medium_message


def test_embed_extract_short_message(gray_image, short_message):
    algo = DCT()
    stego = algo.embed(gray_image, short_message)
    assert algo.extract(stego) == short_message


def test_message_too_large_raises(gray_image):
    algo = DCT()
    # 128x128 grayscale → 16*16 blocks × 5 positions = 1280 bits = 160 bytes max payload
    huge_msg = b"A" * 200
    with pytest.raises(ValueError, match="too large"):
        algo.embed(gray_image, huge_msg)


def test_different_quantization_steps(gray_image, short_message):
    """Both high and low quantization steps should allow correct extraction."""
    for q in [10.0, 50.0]:
        algo = DCT(quantization_step=q)
        stego = algo.embed(gray_image, short_message)
        assert algo.extract(stego) == short_message, f"Failed with q={q}"


# ------------------------------------------------------------------ invisibility (PSNR)

def test_psnr_acceptable(gray_image, short_message):
    """DCT embedding should yield PSNR > 30 dB (noticeable but acceptable for comparison)."""
    algo = DCT()
    stego = algo.embed(gray_image, short_message)
    score = psnr(gray_image, stego)
    print(f"\n[DCT] PSNR = {score:.2f} dB")
    assert score > 30.0


def test_psnr_lower_with_higher_alpha(gray_image, short_message):
    """Larger quantization step → more visible distortion → lower PSNR."""
    algo_low = DCT(quantization_step=10.0)
    algo_high = DCT(quantization_step=50.0)

    stego_low = algo_low.embed(gray_image, short_message)
    stego_high = algo_high.embed(gray_image, short_message)

    psnr_low = psnr(gray_image, stego_low)
    psnr_high = psnr(gray_image, stego_high)
    print(f"\n[DCT] PSNR q=10: {psnr_low:.2f} dB  |  q=50: {psnr_high:.2f} dB")

    assert psnr_low > psnr_high


# ------------------------------------------------------------------ capacity (bpp)

def test_capacity_bpp(gray_image, medium_message):
    bpp = capacity_bpp(gray_image, len(medium_message) * 8)
    print(f"\n[DCT] bpp = {bpp:.4f}")
    assert bpp > 0


# ------------------------------------------------------------------ robustness (BER)

def test_robustness_report(gray_image, medium_message, medium_message_bits):
    algo = DCT()
    stego = algo.embed(gray_image, medium_message)

    def extract_fn(attacked_img):
        try:
            return algo.extract(attacked_img)
        except ValueError:
            return b""

    report = robustness_report(stego, medium_message_bits, extract_fn)
    print("\n[DCT] Robustness report:")
    for attack, score in report.items():
        print(f"  {attack}: BER = {score}")

    assert "jpeg_q75" in report
    assert "gaussian_noise" in report
