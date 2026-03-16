"""
Reed-Solomon encoding/decoding wrapper around the `reedsolo` library.
"""

from reedsolo import RSCodec, ReedSolomonError


def rs_encode(data: bytes, ecc_symbols: int = 10) -> bytes:
    """Encode data with Reed-Solomon ECC.

    Returns the original data + ecc_symbols error-correction bytes.
    Output length: len(data) + ecc_symbols.
    """
    rsc = RSCodec(ecc_symbols)
    return bytes(rsc.encode(data))


def rs_decode(data: bytes, ecc_symbols: int = 10) -> bytes:
    """Decode and correct a Reed-Solomon encoded payload.

    Raises ReedSolomonError if the data is too corrupted to recover.
    """
    rsc = RSCodec(ecc_symbols)
    decoded, _, _ = rsc.decode(data)
    return bytes(decoded)
