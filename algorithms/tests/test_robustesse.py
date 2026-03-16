"""
Tests for the robustesse module (RobustCodec, Reed-Solomon, repetition)
and for the robust=True flag on each steganography algorithm.
"""

import sys
import os

import pytest
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.robustesse import RobustCodec, rs_encode, rs_decode, majority_vote
from src.lsb import LSB
from src.dct import DCT
from src.spread_spectrum import SpreadSpectrum


# ------------------------------------------------------------------ fixtures

@pytest.fixture
def rgb_image():
    rng = np.random.default_rng(42)
    data = rng.integers(30, 220, (256, 256, 3), dtype=np.uint8)
    return Image.fromarray(data, "RGB")


@pytest.fixture
def large_image():
    rng = np.random.default_rng(0)
    data = rng.integers(30, 220, (512, 512, 3), dtype=np.uint8)
    return Image.fromarray(data, "RGB")


@pytest.fixture
def message():
    return b"Hello robustesse!"


# ================================================================== codec unit tests

class TestReedSolomon:
    def test_encode_decode_roundtrip(self):
        data = b"test payload"
        encoded = rs_encode(data, ecc_symbols=10)
        assert len(encoded) == len(data) + 10
        assert rs_decode(encoded, ecc_symbols=10) == data

    def test_corrects_errors(self):
        data = b"correct me"
        encoded = bytearray(rs_encode(data, ecc_symbols=10))
        # Corrupt 4 bytes (RS can correct up to ecc_symbols//2 = 5 byte errors)
        encoded[0] ^= 0xFF
        encoded[3] ^= 0xAA
        encoded[7] ^= 0x55
        encoded[9] ^= 0x0F
        assert rs_decode(bytes(encoded), ecc_symbols=10) == data


class TestMajorityVote:
    def test_clean_copies(self):
        data = b"\xAB\xCD"
        copies = [data, data, data]
        assert majority_vote(copies) == data

    def test_one_corrupted_copy(self):
        original = b"\xFF\x00"
        corrupted = b"\x00\xFF"
        copies = [original, original, corrupted]
        assert majority_vote(copies) == original

    def test_two_vs_one(self):
        a = bytes([0b10101010])
        b_val = bytes([0b01010101])
        # 2 copies of a vs 1 of b → a wins
        assert majority_vote([a, a, b_val]) == a


class TestRobustCodec:
    def test_roundtrip(self):
        codec = RobustCodec(repetitions=3, ecc_symbols=10)
        msg = b"roundtrip test"
        assert codec.decode(codec.encode(msg)) == msg

    def test_encoded_length(self):
        codec = RobustCodec(repetitions=3, ecc_symbols=10)
        msg = b"hello"
        encoded = codec.encode(msg)
        assert len(encoded) == codec.encoded_payload_length(len(msg))

    def test_survives_bit_corruption(self):
        codec = RobustCodec(repetitions=3, ecc_symbols=10)
        msg = b"survive corruption"
        encoded = bytearray(codec.encode(msg))
        # Flip a few bits in the middle of one copy
        mid = len(encoded) // 2
        encoded[mid] ^= 0xFF
        encoded[mid + 1] ^= 0xAA
        result = codec.decode(bytes(encoded))
        assert result == msg

    def test_default_params(self):
        codec = RobustCodec()
        msg = b"default params"
        assert codec.decode(codec.encode(msg)) == msg


# ================================================================== integration: LSB + robust

class TestLSBRobust:
    def test_embed_extract_roundtrip(self, rgb_image, message):
        lsb = LSB()
        stego = lsb.embed(rgb_image, message, robust=True)
        recovered = lsb.extract(stego, robust=True)
        assert recovered == message

    def test_robust_payload_is_larger(self, rgb_image, message):
        """Robust embed uses more bits than plain embed."""
        lsb = LSB()
        stego_plain = lsb.embed(rgb_image, message)
        stego_robust = lsb.embed(rgb_image, message, robust=True)
        assert stego_plain.size == stego_robust.size

    def test_extract_robust_flag_must_match(self, rgb_image, message):
        """Extracting without robust=True from a robust-embedded image returns garbage."""
        lsb = LSB()
        stego = lsb.embed(rgb_image, message, robust=True)
        raw = lsb.extract(stego, robust=False)
        assert raw != message


# ================================================================== integration: DCT + robust

class TestDCTRobust:
    def test_embed_extract_roundtrip(self, rgb_image, message):
        dct = DCT(quantization_step=25.0)
        stego = dct.embed(rgb_image, message, robust=True)
        recovered = dct.extract(stego, robust=True)
        assert recovered == message

    def test_extract_robust_flag_must_match(self, rgb_image, message):
        dct = DCT()
        stego = dct.embed(rgb_image, message, robust=True)
        raw = dct.extract(stego, robust=False)
        assert raw != message


# ================================================================== integration: SpreadSpectrum + robust

class TestSpreadSpectrumRobust:
    def test_embed_extract_roundtrip(self, large_image, message):
        ss = SpreadSpectrum(key="test_key", alpha=5.0)
        stego = ss.embed(large_image, message, robust=True)
        recovered = ss.extract(stego, len(message) + 3, robust=True)
        assert recovered == message

    def test_extract_robust_flag_must_match(self, large_image, message):
        ss = SpreadSpectrum(key="test_key", alpha=5.0)
        stego = ss.embed(large_image, message, robust=True)
        with pytest.raises(Exception):
            ss.extract(stego, len(message) + 3, robust=False)
