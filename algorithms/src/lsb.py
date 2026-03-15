"""
LSB (Least Significant Bit) — Spatial Domain Steganography
Embeds message bits directly into the LSBs of pixel channel values.
"""

import numpy as np
from PIL import Image


class LSB:
    DELIMITER = b"\x00\x00\x00"  # marks end of hidden message

    def embed(self, image: Image.Image, message: bytes) -> Image.Image:
        """Embed a byte message into the LSB of each channel byte."""
        payload = message + self.DELIMITER
        pixels = np.array(image, dtype=np.uint8)
        flat = pixels.flatten()

        bits = self._bytes_to_bits(payload)
        if len(bits) > len(flat):
            raise ValueError(
                f"Message too large: need {len(bits)} bits, image has {len(flat)} channels"
            )

        for i, bit in enumerate(bits):
            flat[i] = (flat[i] & 0xFE) | bit

        return Image.fromarray(flat.reshape(pixels.shape), image.mode)

    def extract(self, image: Image.Image) -> bytes:
        """Extract the hidden message from the LSBs."""
        flat = np.array(image, dtype=np.uint8).flatten()
        bits = [int(b) & 1 for b in flat]
        return self._bits_to_bytes_until_delimiter(bits)

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _bytes_to_bits(data: bytes) -> list[int]:
        return [int(b) for byte in data for b in f"{byte:08b}"]

    def _bits_to_bytes_until_delimiter(self, bits: list[int]) -> bytes:
        result = bytearray()
        delimiter_bits = self._bytes_to_bits(self.DELIMITER)

        for i in range(0, len(bits) - 7, 8):
            byte = int("".join(str(b) for b in bits[i : i + 8]), 2)
            result.append(byte)
            # check for delimiter at the end of accumulated bytes
            if len(result) >= len(self.DELIMITER):
                tail_bits = self._bytes_to_bits(bytes(result[-len(self.DELIMITER) :]))
                if tail_bits == delimiter_bits:
                    return bytes(result[: -len(self.DELIMITER)])

        raise ValueError("Delimiter not found — no hidden message or corrupted image")
