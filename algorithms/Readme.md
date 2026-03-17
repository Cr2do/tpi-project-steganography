# secure-stegano

Python steganography library implementing three algorithms (LSB, DCT, Spread Spectrum) with an optional error-correction layer (Reed-Solomon + repetition coding) and objective quality metrics.

## Installation

```bash
pip install secure-stegano
```

## Algorithms

### LSB — Least Significant Bit (Spatial Domain)

Embeds message bits directly into the least significant bit of each pixel channel. Fast and high-capacity, but fragile against image processing.

```python
from PIL import Image
from tpi_stegano import LSB

lsb = LSB()
cover = Image.open("cover.png")

stego = lsb.embed(cover, b"secret message")
message = lsb.extract(stego)  # b"secret message"
```

### DCT — Discrete Cosine Transform (Frequency Domain)

Embeds bits into the mid-frequency DCT coefficients of 8×8 pixel blocks, inspired by JPEG steganography (JSteg/F5 principle). More resistant to visual detection than LSB.

```python
from tpi_stegano import DCT

dct = DCT(quantization_step=25.0)
stego = dct.embed(cover, b"secret message")
message = dct.extract(stego)
```

### Spread Spectrum (Frequency Domain)

Spreads each message bit across the entire DCT spectrum of the image using a pseudo-random carrier sequence derived from a secret key. Most robust algorithm against noise, filtering and compression.

```python
from tpi_stegano import SpreadSpectrum

ss = SpreadSpectrum(key="my_secret_key", alpha=5.0)
stego = ss.embed(cover, b"secret message")
message = ss.extract(stego, message_length_bytes=len(b"secret message") + 3)
```

## Robustness Layer

All three algorithms support an optional `robust=True` mode that applies **Reed-Solomon error correction** combined with **repetition coding** before embedding. This allows message recovery even after JPEG compression, Gaussian noise, cropping, rotation or blur.

```python
# Embed with error correction
stego = lsb.embed(cover, b"secret message", robust=True)

# Extract — must use the same robust flag
message = lsb.extract(stego, robust=True)  # b"secret message"
```

The `RobustCodec` can also be used independently:

```python
from tpi_stegano import RobustCodec

codec = RobustCodec(repetitions=3, ecc_symbols=10)
encoded = codec.encode(b"secret message")
recovered = codec.decode(encoded)  # b"secret message"
```

## Quality Metrics

Objective metrics to evaluate and compare algorithm performance.

```python
from tpi_stegano import psnr, capacity_bpp, ber, robustness_report

# Invisibility — higher is better (>40 dB = imperceptible)
score = psnr(cover, stego)

# Capacity — bits embedded per pixel
bpp = capacity_bpp(cover, message_bits=len(b"secret message") * 8)

# Bit Error Rate — 0.0 = perfect, 0.5 = random noise
error_rate = ber(original_bits, recovered_bits)

# Full robustness report across 6 attacks (JPEG, noise, crop, rotation, blur)
report = robustness_report(stego, original_bits, extract_fn=lambda img: lsb.extract(img))
# {
#   "jpeg_q75": 0.0,
#   "jpeg_q50": 0.04,
#   "gaussian_noise": 0.0,
#   "crop_10pct": 0.12,
#   "rotation_5deg": 0.21,
#   "blur": 0.0
# }
```

## Algorithm Comparison

| | LSB | DCT | Spread Spectrum |
|---|---|---|---|
| Domain | Spatial | Frequency | Frequency |
| Capacity | High | Medium | Low |
| Invisibility (PSNR) | ~50 dB | ~40 dB | ~35 dB |
| JPEG resistance | Fragile | Good | Best |
| Noise resistance | Fragile | Medium | Best |
| Requires key | No | No | Yes |

## Dependencies

- `numpy >= 1.24`
- `Pillow >= 10.0`
- `scipy >= 1.11`
- `reedsolo >= 1.7`

## License

MIT
