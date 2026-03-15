"""
Spread Spectrum — Frequency Domain Steganography
Each message bit is spread across many DCT coefficients of the full image
using a pseudo-random key (PRNG-generated carrier sequence).
More robust than LSB/DCT against noise and filtering.
"""

import hashlib
import numpy as np
from PIL import Image
from scipy.fft import dctn, idctn


DELIMITER = b"\x00\x00\x00"


class SpreadSpectrum:
    def __init__(self, key: str = "default_key", alpha: float = 5.0):
        """
        key   – secret key used to generate the pseudo-random carrier
        alpha – embedding strength (higher = more robust, less invisible)
        """
        self.key = key
        self.alpha = alpha

    # ------------------------------------------------------------------ public

    def embed(self, image: Image.Image, message: bytes) -> Image.Image:
        """Embed message using spread-spectrum in the DCT domain."""
        gray = np.array(image.convert("L"), dtype=np.float64)
        coeffs = dctn(gray, norm="ortho")
        flat_coeffs = coeffs.flatten()

        payload = message + DELIMITER
        bits = _bytes_to_bits(payload)
        bipolar = [1 if b else -1 for b in bits]  # convert {0,1} → {-1,+1}

        carriers = self._generate_carriers(len(bipolar), len(flat_coeffs))

        for i, bit_val in enumerate(bipolar):
            flat_coeffs += self.alpha * bit_val * carriers[i]

        stego_coeffs = flat_coeffs.reshape(coeffs.shape)
        stego = np.clip(idctn(stego_coeffs, norm="ortho"), 0, 255).astype(np.uint8)
        return Image.fromarray(stego, "L").convert(image.mode)

    def extract(self, image: Image.Image, message_length_bytes: int) -> bytes:
        """
        Extract hidden message.
        message_length_bytes must include the 3-byte delimiter (len(msg) + 3).
        """
        gray = np.array(image.convert("L"), dtype=np.float64)
        flat_coeffs = dctn(gray, norm="ortho").flatten()

        total_bits = (message_length_bytes + len(DELIMITER)) * 8
        carriers = self._generate_carriers(total_bits, len(flat_coeffs))

        bits = []
        for i in range(total_bits):
            correlation = float(np.dot(flat_coeffs, carriers[i]))
            bits.append(1 if correlation > 0 else 0)

        return _bits_to_bytes_until_delimiter(bits)

    # ------------------------------------------------------------------ helpers

    def _generate_carriers(self, n_bits: int, n_coeffs: int) -> np.ndarray:
        """Generate n_bits orthogonal-ish PRNG carriers of length n_coeffs."""
        seed = int(hashlib.sha256(self.key.encode()).hexdigest(), 16) % (2**32)
        rng = np.random.default_rng(seed)
        carriers = rng.standard_normal((n_bits, n_coeffs))
        # normalise each carrier to unit length
        norms = np.linalg.norm(carriers, axis=1, keepdims=True)
        return carriers / norms


# ------------------------------------------------------------------ module helpers

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
