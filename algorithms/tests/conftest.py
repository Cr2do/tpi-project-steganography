"""
Shared pytest fixtures: synthetic test images and sample messages.
No external image files needed — everything is generated in memory.
"""

import numpy as np
import pytest
from PIL import Image


MESSAGE_SHORT = b"Hi!"
MESSAGE_MEDIUM = b"Steganography test message 1234"
MESSAGE_BITS_MEDIUM = [int(b) for byte in MESSAGE_MEDIUM for b in f"{byte:08b}"]


def _make_image(width: int = 128, height: int = 128, mode: str = "RGB") -> Image.Image:
    """Create a synthetic image with realistic pixel variation."""
    rng = np.random.default_rng(42)
    arr = rng.integers(30, 220, (height, width, 3), dtype=np.uint8)
    img = Image.fromarray(arr, "RGB")
    return img.convert(mode)


@pytest.fixture
def rgb_image():
    return _make_image(mode="RGB")


@pytest.fixture
def gray_image():
    return _make_image(mode="L")


@pytest.fixture
def large_image():
    """512x512 for robustness / capacity tests."""
    return _make_image(width=512, height=512, mode="RGB")


@pytest.fixture
def short_message():
    return MESSAGE_SHORT


@pytest.fixture
def medium_message():
    return MESSAGE_MEDIUM


@pytest.fixture
def medium_message_bits():
    return MESSAGE_BITS_MEDIUM
