"""
RobustCodec: combines Reed-Solomon ECC + repetition for steganography payload protection.

Encoding pipeline:
    message → RS encode → [length header + RS data] repeated n times → encoded payload

Payload wire format (before the steganography DELIMITER):
    [ rs_length: 2 bytes ] × repetitions  +  [ RS-encoded message ] × repetitions

    Where rs_length = len(message) + ecc_symbols.

Decoding pipeline:
    encoded payload → majority-vote header → parse rs_length
                    → majority-vote RS data → RS decode → message
"""

from .reed_solomon import rs_encode, rs_decode
from .repetition import majority_vote


class RobustCodec:
    def __init__(self, repetitions: int = 3, ecc_symbols: int = 10):
        """
        repetitions  – number of times the RS-encoded payload is repeated
        ecc_symbols  – number of Reed-Solomon error-correction bytes (max correctable
                       errors = ecc_symbols // 2 bytes)
        """
        self.repetitions = repetitions
        self.ecc_symbols = ecc_symbols

    # ------------------------------------------------------------------ public

    def encode(self, message: bytes) -> bytes:
        """Encode a message into a robust payload ready to be embedded.

        Returns a bytes object that can be passed directly to the steganography
        algorithm's embed method (the algo will still append its own DELIMITER).
        """
        rs_encoded = rs_encode(message, self.ecc_symbols)
        rs_length = len(rs_encoded)

        # 2-byte big-endian length header, repeated for protection
        header = rs_length.to_bytes(2, "big")
        payload = header * self.repetitions + rs_encoded * self.repetitions
        return payload

    def decode(self, data: bytes) -> bytes:
        """Decode a robust payload back to the original message.

        ``data`` must be the raw bytes extracted by the steganography algorithm
        (DELIMITER already stripped by the extractor).
        """
        header_total = 2 * self.repetitions

        # Recover rs_length via majority vote over header copies
        header_copies = [data[i * 2 : (i + 1) * 2] for i in range(self.repetitions)]
        header = majority_vote(header_copies)
        rs_length = int.from_bytes(header, "big")

        # Recover RS-encoded data via majority vote over payload copies
        base = header_total
        rs_copies = [
            data[base + i * rs_length : base + (i + 1) * rs_length]
            for i in range(self.repetitions)
        ]
        rs_encoded = majority_vote(rs_copies)

        return rs_decode(rs_encoded, self.ecc_symbols)

    def encoded_payload_length(self, message_length: int) -> int:
        """Return the byte length that encode() will produce for a given message length.

        Useful for SpreadSpectrum which needs to know how many bits to extract.
        """
        rs_length = message_length + self.ecc_symbols
        return 2 * self.repetitions + rs_length * self.repetitions
