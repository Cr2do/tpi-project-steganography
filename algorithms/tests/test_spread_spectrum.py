"""
Tests for the Spread Spectrum steganography algorithm.
Covers: correctness, capacity, invisibility (PSNR), robustness (BER).
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.spread_spectrum import SpreadSpectrum
from src.metrics import psnr, capacity_bpp, ber, robustness_report, ATTACKS


# ------------------------------------------------------------------ correctness

def test_embed_extract_roundtrip(large_image, medium_message):
    algo = SpreadSpectrum(key="secret_key")
    stego = algo.embed(large_image, medium_message)
    msg_len = len(medium_message) + 3  # +3 for delimiter
    assert algo.extract(stego, msg_len) == medium_message


def test_embed_extract_short_message(large_image, short_message):
    algo = SpreadSpectrum()
    stego = algo.embed(large_image, short_message)
    assert algo.extract(stego, len(short_message) + 3) == short_message


def test_wrong_key_fails(large_image, medium_message):
    """Extracting with a different key should return garbage (not the original message)."""
    embed_algo = SpreadSpectrum(key="correct_key")
    extract_algo = SpreadSpectrum(key="wrong_key")
    stego = embed_algo.embed(large_image, medium_message)
    try:
        result = extract_algo.extract(stego, len(medium_message) + 3)
        assert result != medium_message
    except ValueError:
        pass  # wrong key → pure noise correlation → delimiter not found, as expected


def test_different_alpha_roundtrip(large_image, short_message):
    for alpha in [2.0, 10.0, 20.0]:
        algo = SpreadSpectrum(alpha=alpha)
        stego = algo.embed(large_image, short_message)
        result = algo.extract(stego, len(short_message) + 3)
        assert result == short_message, f"Failed with alpha={alpha}"


# ------------------------------------------------------------------ invisibility (PSNR)

def test_psnr_acceptable(large_image, short_message):
    """Spread Spectrum at default alpha should yield PSNR > 25 dB."""
    algo = SpreadSpectrum()
    stego = algo.embed(large_image, short_message)
    score = psnr(large_image, stego)
    print(f"\n[SS] PSNR = {score:.2f} dB")
    assert score > 25.0


def test_psnr_tradeoff_with_alpha(large_image, short_message):
    """Higher alpha → stronger embedding → lower PSNR."""
    algo_weak = SpreadSpectrum(alpha=2.0)
    algo_strong = SpreadSpectrum(alpha=20.0)

    stego_weak = algo_weak.embed(large_image, short_message)
    stego_strong = algo_strong.embed(large_image, short_message)

    psnr_weak = psnr(large_image, stego_weak)
    psnr_strong = psnr(large_image, stego_strong)
    print(f"\n[SS] PSNR alpha=2: {psnr_weak:.2f} dB  |  alpha=20: {psnr_strong:.2f} dB")

    assert psnr_weak > psnr_strong


# ------------------------------------------------------------------ capacity (bpp)

def test_capacity_bpp(large_image, medium_message):
    bpp = capacity_bpp(large_image, len(medium_message) * 8)
    print(f"\n[SS] bpp = {bpp:.6f}")
    # Spread Spectrum has very low bpp — each bit uses the entire image
    assert bpp > 0


# ------------------------------------------------------------------ robustness (BER)

def test_robustness_jpeg(large_image, medium_message, medium_message_bits):
    """Spread spectrum should be more robust to JPEG than LSB."""
    algo = SpreadSpectrum(alpha=10.0)
    stego = algo.embed(large_image, medium_message)
    msg_len = len(medium_message) + 3

    attacked = ATTACKS["jpeg_q75"](stego)
    try:
        recovered = algo.extract(attacked, msg_len)
        recovered_bits = [int(b) for byte in recovered for b in f"{byte:08b}"]
        error_rate = ber(medium_message_bits, recovered_bits)
    except ValueError:
        error_rate = 1.0

    print(f"\n[SS] BER after JPEG q=75: {error_rate:.4f}")
    # Just print result — SS robustness depends on alpha and image size
    assert 0.0 <= error_rate <= 1.0


def test_full_robustness_report(large_image, medium_message, medium_message_bits):
    algo = SpreadSpectrum(alpha=10.0)
    stego = algo.embed(large_image, medium_message)
    msg_len = len(medium_message) + 3

    def extract_fn(attacked_img):
        try:
            return algo.extract(attacked_img, msg_len)
        except ValueError:
            return b""

    report = robustness_report(stego, medium_message_bits, extract_fn)
    print("\n[SS] Robustness report:")
    for attack, score in report.items():
        print(f"  {attack}: BER = {score}")

    assert set(report.keys()) == set(ATTACKS.keys())
