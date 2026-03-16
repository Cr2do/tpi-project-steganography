"""
Repetition code: encodes data by repeating it n times and
decodes via bitwise majority vote across all copies.
"""


def repeat_encode(data: bytes, repetitions: int = 3) -> bytes:
    """Repeat ``data`` exactly ``repetitions`` times."""
    return data * repetitions


def majority_vote(copies: list[bytes]) -> bytes:
    """Recover bytes by bitwise majority vote across multiple copies.

    For each bit position, the output bit is 1 if more than half of the
    copies have a 1 at that position, else 0.
    """
    n = len(copies)
    if n == 0:
        return b""
    length = min(len(c) for c in copies)
    result = bytearray(length)
    for i in range(length):
        for bit_pos in range(8):
            votes = sum(1 for c in copies if (c[i] >> (7 - bit_pos)) & 1)
            if votes > n / 2:
                result[i] |= 1 << (7 - bit_pos)
    return bytes(result)


def repeat_decode(data: bytes, repetitions: int = 3) -> bytes:
    """Split ``data`` into ``repetitions`` equal chunks and majority-vote them.

    Raises ValueError if ``len(data)`` is not divisible by ``repetitions``.
    """
    if len(data) % repetitions != 0:
        raise ValueError(
            f"Data length {len(data)} is not divisible by repetitions={repetitions}"
        )
    chunk_size = len(data) // repetitions
    copies = [data[i * chunk_size : (i + 1) * chunk_size] for i in range(repetitions)]
    return majority_vote(copies)
