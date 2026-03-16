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
from .robustesse import RobustCodec


DELIMITER = b"\x00\x00\x00"


class SpreadSpectrum:
    def __init__(self, key: str = "default_key", alpha: float = 5.0):
        """
        key   – secret key used to generate the pseudo-random carrier
        alpha – embedding strength (higher = more robust, less invisible)
        """
        self.key = key
        self.alpha = alpha
        self._orig_coeffs: np.ndarray | None = None  # stored during embed for blind extraction

    # ------------------------------------------------------------------ public

    def embed(self, image: Image.Image, message: bytes, robust: bool = False) -> Image.Image:
        """Embed message using spread-spectrum in the DCT domain.

        Args:
            image: Cover image.
            message: Bytes to hide.
            robust: If True, apply Reed-Solomon + repetition coding before embedding.
        """
        if robust:
            message = RobustCodec().encode(message)

        gray = np.array(image.convert("L"), dtype=np.float64)
        coeffs = dctn(gray, norm="ortho")
        self._orig_coeffs = coeffs.flatten().copy()  # keep original for extraction
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

    def extract(
        self,
        image: Image.Image,
        message_length_bytes: int,
        robust: bool = False,
    ) -> bytes:
        """Extract hidden message.

        Args:
            image: Stego image (possibly attacked).
            message_length_bytes: Original message length **including** the 3-byte
                delimiter (i.e. ``len(original_message) + 3``).
                When ``robust=True`` this is still the *original* message length;
                the actual embedded length is computed internally.
            robust: Must match the flag used during embed.
        """
        gray = np.array(image.convert("L"), dtype=np.float64)
        stego_coeffs = dctn(gray, norm="ortho").flatten()

        # Subtract the original DCT to isolate the embedded signal.
        if self._orig_coeffs is not None and self._orig_coeffs.shape == stego_coeffs.shape:
            flat_coeffs = stego_coeffs - self._orig_coeffs
        else:
            flat_coeffs = stego_coeffs  # fallback: wrong key / no stored original → garbage

        if robust:
            codec = RobustCodec()
            actual_length = codec.encoded_payload_length(message_length_bytes - 3) + 3
        else:
            actual_length = message_length_bytes

        total_bits = actual_length * 8
        carriers = self._generate_carriers(total_bits, len(flat_coeffs))

        bits = []
        for i in range(total_bits):
            correlation = float(np.dot(flat_coeffs, carriers[i]))
            bits.append(1 if correlation > 0 else 0)

        raw = _bits_to_bytes_until_delimiter(bits)

        if robust:
            return RobustCodec().decode(raw)
        return raw

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
