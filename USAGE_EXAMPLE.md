# Using audio/ogg;codecs=opus with Counterparty Inscriptions

## Overview

This fork now supports `audio/ogg;codecs=opus` MIME type for creating inscriptions with Counterparty tokens. This allows you to inscribe audio files (like music, podcasts, voice recordings) directly on Bitcoin using the Ordinals protocol combined with Counterparty tokens.

## What Changed

### 1. MIME Type Support
- Added `audio/ogg` to the list of supported MIME types
- Added support for codec parameters (e.g., `;codecs=opus`)
- Maintained backward compatibility with all existing MIME types

### 2. Files Modified
- `/counterparty-core/counterpartycore/lib/utils/helpers.py`
  - Added `_init_custom_mimetypes()` function to register OGG formats
  - Added `parse_mime_type()` function to handle codec parameters
  - Updated `check_content()` to validate MIME types with parameters

## Usage Examples

### Example 1: Token Issuance with Audio Inscription

```python
# Using the Counterparty API to create a token with an audio inscription

params = {
    "source": "your_bitcoin_address",
    "asset": "MYAUDIOTOKEN",
    "quantity": 1000000000,  # 10 tokens (8 decimals)
    "divisible": True,
    "description": "hex_encoded_audio_data",  # Your OGG/Opus audio file as hex
    "mime_type": "audio/ogg;codecs=opus",
}

construct_params = {
    "encoding": "taproot",
    "inscription": True,  # Enable inscription
    "sat_per_vbyte": 10,
}

# Compose the transaction
result = api.compose_issuance(params, construct_params)
```

### Example 2: Fairminter with Audio Content

```python
params = {
    "source": "your_bitcoin_address",
    "asset": "A95428959745315389",  # Numeric asset
    "price": 100000000,  # 1 XCP per mint
    "hard_cap": 100 * 10**8,
    "description": "hex_encoded_audio_data",
    "mime_type": "audio/ogg;codecs=opus",
    "start_block": current_block + 10,
}

construct_params = {
    "encoding": "taproot",
    "inscription": True,
}

result = api.compose_fairminter(params, construct_params)
```

### Example 3: Broadcast with Audio

```python
params = {
    "source": "your_bitcoin_address",
    "text": "hex_encoded_audio_data",
    "value": 0,
    "fee_fraction": 0,
    "mime_type": "audio/ogg;codecs=opus",
}

construct_params = {
    "encoding": "taproot",
    "inscription": True,
}

result = api.compose_broadcast(params, construct_params)
```

## Supported Audio MIME Types

After this update, the following audio MIME types are supported:

| MIME Type | With Codecs | Description |
|-----------|-------------|-------------|
| `audio/ogg` | ✅ | OGG audio container |
| `audio/ogg;codecs=opus` | ✅ | OGG with Opus codec |
| `audio/ogg;codecs=vorbis` | ✅ | OGG with Vorbis codec |
| `audio/opus` | ✅ | Opus audio (already supported) |
| `audio/mpeg` | ✅ | MP3 audio (already supported) |
| `audio/wav` | ✅ | WAV audio (already supported) |

## Preparing Audio Files

### Converting Audio to OGG/Opus

Use `ffmpeg` to convert audio files to OGG with Opus codec:

```bash
# Convert any audio file to OGG/Opus
ffmpeg -i input.mp3 -c:a libopus -b:a 128k output.ogg

# For voice/speech (lower bitrate)
ffmpeg -i input.wav -c:a libopus -b:a 64k -application voip output.ogg

# For music (higher quality)
ffmpeg -i input.flac -c:a libopus -b:a 192k -application audio output.ogg
```

### Converting to Hex for Inscription

```bash
# Convert OGG file to hex string
xxd -p output.ogg | tr -d '\n' > output.hex

# Or using Python
python3 -c "import sys; print(open('output.ogg', 'rb').read().hex())" > output.hex
```

### Size Considerations

- Bitcoin transactions have size limits
- Larger files = higher transaction fees
- Consider compressing audio appropriately:
  - Voice/Speech: 32-64 kbps Opus
  - Music: 96-192 kbps Opus
  - Maximum recommended: ~400KB for reasonable fees

## Technical Details

### Inscription Envelope Format

When `inscription=True` is set, the transaction uses the Ordinals inscription format:

```
OP_FALSE
OP_IF
  "ord"
  0x07
  "xcp"
  0x01
  <mime_type>              # e.g., "audio/ogg;codecs=opus"
  0x05
  <metadata_chunk_1>       # CBOR-encoded Counterparty data
  0x05
  <metadata_chunk_2>
  ...
  OP_0
  <content_chunk_1>        # Your audio file data
  <content_chunk_2>
  ...
OP_ENDIF
<pubkey>
OP_CHECKSIG
```

### Metadata Structure

The metadata is CBOR-encoded and includes:
- Message type ID (e.g., issuance, fairminter)
- Token parameters (asset name, quantity, etc.)
- All Counterparty protocol data

### Content Storage

- Audio content is stored as binary data
- Split into 520-byte chunks for script compatibility
- Full content is reconstructed when reading the inscription

## Querying Inscriptions

After the transaction is confirmed, you can query the inscription:

```python
# Get asset information including MIME type
result = api.get_asset("MYAUDIOTOKEN")
print(result["mime_type"])  # "audio/ogg;codecs=opus"

# Get the inscription content
result = api.get_asset_info("MYAUDIOTOKEN")
content_hex = result["description"]
audio_bytes = bytes.fromhex(content_hex)

# Save to file
with open("recovered_audio.ogg", "wb") as f:
    f.write(audio_bytes)
```

## Testing

Run the test suite to verify functionality:

```bash
# Run the custom audio/ogg test
python3 test_audio_ogg.py

# Run the full Counterparty test suite
cd counterparty-core
pytest counterpartycore/test/
```

## Benefits of OGG/Opus

1. **Efficient Compression**: Opus provides excellent quality at low bitrates
2. **Open Standard**: Royalty-free, open-source codec
3. **Versatile**: Works well for both speech and music
4. **Modern**: Designed for internet streaming and real-time applications
5. **Lower Fees**: Better compression = smaller files = lower Bitcoin transaction fees

## Limitations

- Maximum practical file size: ~400KB (due to Bitcoin transaction limits)
- Larger inscriptions require higher fees
- Content is immutable once inscribed
- Must be valid OGG/Opus format (validate before inscribing)

## Best Practices

1. **Test First**: Always test with small amounts on testnet
2. **Validate Audio**: Ensure your OGG file is valid before converting to hex
3. **Optimize Size**: Use appropriate bitrates for your content type
4. **Check Fees**: Calculate transaction fees before inscribing large files
5. **Backup Data**: Keep original files; inscriptions are permanent but wallets can be lost

## Support

For issues or questions:
- Check the [Counterparty Documentation](https://docs.counterparty.io)
- Review the test files in `/counterparty-core/counterpartycore/test/`
- See `AUDIO_OGG_ANALYSIS.md` for technical implementation details
