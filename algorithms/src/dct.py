"""
DCT (Discrete Cosine Transform) — Frequency Domain Steganography
Embeds message bits into mid-frequency DCT coefficients of 8x8 image blocks.
Inspired by JPEG steganography (similar to JSteg/F5 principle).
"""

import numpy as np
from PIL import Image
from scipy.fft import dctn, idctn
from .robustesse import RobustCodec


# Mid-frequency coefficients used for embedding (avoids DC and high-freq)
_EMBED_POSITIONS = [(1, 2), (2, 1), (2, 2), (1, 3), (3, 1)]

DELIMITER = b"\x00\x00\x00"


class DCT:
    def __init__(self, quantization_step: float = 25.0):
        # Larger step = more robust but less invisible
        self.q = quantization_step

    def embed(self, image: Image.Image, message: bytes, robust: bool = False) -> Image.Image:
        """Embed message bits into mid-frequency DCT coefficients.

        Args:
            image: Cover image.
            message: Bytes to hide.
            robust: If True, apply Reed-Solomon + repetition coding before embedding.
        """
        if robust:
            message = RobustCodec().encode(message)

        gray = np.array(image.convert("L"), dtype=np.float64)
        payload = message + DELIMITER
        bits = _bytes_to_bits(payload)

        h, w = gray.shape
        bit_idx = 0

        for row in range(0, h - 7, 8):
            for col in range(0, w - 7, 8):
                block = gray[row : row + 8, col : col + 8]
                coeffs = dctn(block, norm="ortho")

                for r, c in _EMBED_POSITIONS:
                    if bit_idx >= len(bits):
                        break
                    # quantize coefficient, replace LSB with message bit
                    q_val = int(round(coeffs[r, c] / self.q))
                    q_val = (q_val & ~1) | bits[bit_idx]
                    coeffs[r, c] = q_val * self.q
                    bit_idx += 1

                gray[row : row + 8, col : col + 8] = idctn(coeffs, norm="ortho")

                if bit_idx >= len(bits):
                    break
            if bit_idx >= len(bits):
                break

        if bit_idx < len(bits):
            raise ValueError(
                f"Message too large: need {len(bits)} bits, image can hold ~{bit_idx} bits"
            )

        stego = np.clip(gray, 0, 255).astype(np.uint8)
        return Image.fromarray(stego, "L").convert(image.mode)

    def extract(self, image: Image.Image, robust: bool = False) -> bytes:
        """Extract hidden bits from DCT coefficients.

        Args:
            image: Stego image (possibly attacked).
            robust: Must match the flag used during embed.
        """
        gray = np.array(image.convert("L"), dtype=np.float64)
        h, w = gray.shape
        bits: list[int] = []

        for row in range(0, h - 7, 8):
            for col in range(0, w - 7, 8):
                block = gray[row : row + 8, col : col + 8]
                coeffs = dctn(block, norm="ortho")

                for r, c in _EMBED_POSITIONS:
                    q_val = int(round(coeffs[r, c] / self.q))
                    bits.append(q_val & 1)

        raw = _bits_to_bytes_until_delimiter(bits)

        if robust:
            return RobustCodec().decode(raw)
        return raw


# ------------------------------------------------------------------ helpers

def _bytes_to_bits(data: bytes) -> list[int]:
    return [int(b) for byte in data for b in f"{byte:08b}"]


def _bits_to_bytes_until_delimiter(bits: list[int]) -> bytes:
    delimiter_bits = _bytes_to_bits(DELIMITER)
    result = bytearray()

    for i in range(0, len(bits) - 7, 8):
        byte = int("".join(str(b) for b in bits[i : i + 8]), 2)
        result.append(byte)
        if len(result) >= len(DELIMITER):
            if list(_bytes_to_bits(bytes(result[-len(DELIMITER) :]))) == delimiter_bits:
                return bytes(result[: -len(DELIMITER)])

    raise ValueError("Delimiter not found — no hidden message or corrupted image")
