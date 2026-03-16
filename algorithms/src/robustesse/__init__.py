"""
robustesse – Error-correction layer for steganography payloads.

Combines Reed-Solomon ECC and repetition coding so that embedded messages
can survive image attacks (JPEG compression, noise, cropping …).

Usage example:
    from algorithms.src.robustesse import RobustCodec

    codec = RobustCodec(repetitions=3, ecc_symbols=10)
    encoded = codec.encode(b"secret message")
    recovered = codec.decode(encoded)   # b"secret message"
"""

from .codec import RobustCodec
from .reed_solomon import rs_encode, rs_decode
from .repetition import repeat_encode, repeat_decode, majority_vote

__all__ = [
    "RobustCodec",
    "rs_encode",
    "rs_decode",
    "repeat_encode",
    "repeat_decode",
    "majority_vote",
]
