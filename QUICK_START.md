# Quick Start: Audio Inscriptions with Counterparty

## TL;DR

This fork now supports `audio/ogg;codecs=opus` for Bitcoin inscriptions with Counterparty tokens.

## Quick Test

```bash
# Verify the implementation works
cd /home/node/tatiana/fork2/counterparty-core
python3 test_audio_ogg.py
```

Expected output: ✅ ALL TESTS PASSED!

## Create an Audio Inscription

### Step 1: Prepare Your Audio File

```bash
# Convert audio to OGG/Opus (if needed)
ffmpeg -i your_audio.mp3 -c:a libopus -b:a 128k output.ogg

# Convert to hex
xxd -p output.ogg | tr -d '\n' > audio.hex
```

### Step 2: Create Token with Inscription

```python
from counterpartycore.lib import api

# Your audio data as hex string
audio_hex = open('audio.hex', 'r').read()

# Create token with audio inscription
params = {
    "source": "your_bitcoin_address",
    "asset": "MYAUDIO",
    "quantity": 100000000,  # 1 token
    "divisible": True,
    "description": audio_hex,
    "mime_type": "audio/ogg;codecs=opus",
}

construct_params = {
    "encoding": "taproot",
    "inscription": True,
    "sat_per_vbyte": 10,
}

result = api.compose_issuance(params, construct_params)
```

### Step 3: Broadcast Transaction

```python
# Sign and broadcast the transaction
signed_tx = api.sign_transaction(result["rawtransaction"])
txid = api.broadcast_transaction(signed_tx)
print(f"Transaction ID: {txid}")
```

## Supported Formats

✅ `audio/ogg` - Basic OGG audio  
✅ `audio/ogg;codecs=opus` - OGG with Opus codec  
✅ `audio/ogg;codecs=vorbis` - OGG with Vorbis codec  
✅ All existing MIME types (text/*, image/*, etc.)

## File Size Recommendations

| Content Type | Recommended Bitrate | ~1 min file size |
|--------------|---------------------|------------------|
| Voice/Speech | 32-64 kbps | ~240-480 KB |
| Podcast | 64-96 kbps | ~480-720 KB |
| Music | 96-192 kbps | ~720 KB-1.4 MB |

⚠️ **Note**: Larger files = higher Bitcoin transaction fees

## What Changed?

**File Modified**: `/counterparty-core/counterpartycore/lib/utils/helpers.py`

- ✅ Added `audio/ogg` MIME type registration
- ✅ Added codec parameter parsing (`;codecs=opus`)
- ✅ Updated validation to support parameterized MIME types
- ✅ Maintained 100% backward compatibility

## Verify It Works

```bash
# Run the test suite
python3 test_audio_ogg.py

# Run existing tests (ensure no regressions)
cd counterparty-core
python3 -m pytest counterpartycore/test/units/utils/helpers_test.py -v
```

## Documentation

- **AUDIO_OGG_ANALYSIS.md** - Technical analysis
- **IMPLEMENTATION_SUMMARY.md** - Implementation details
- **USAGE_EXAMPLE.md** - Detailed usage guide
- **test_audio_ogg.py** - Test suite

## Need Help?

1. Check `USAGE_EXAMPLE.md` for detailed examples
2. Review `AUDIO_OGG_ANALYSIS.md` for technical details
3. Run `test_audio_ogg.py` to verify your setup
4. See existing tests in `/counterparty-core/counterpartycore/test/`

## Example: Complete Workflow

```bash
# 1. Prepare audio
ffmpeg -i podcast.mp3 -c:a libopus -b:a 64k podcast.ogg
xxd -p podcast.ogg | tr -d '\n' > podcast.hex

# 2. Test the implementation
python3 test_audio_ogg.py

# 3. Create inscription (using counterparty-cli or API)
counterparty-cli compose issuance \
  --source=your_address \
  --asset=PODCAST \
  --quantity=1 \
  --description=$(cat podcast.hex) \
  --mime-type="audio/ogg;codecs=opus" \
  --encoding=taproot \
  --inscription

# 4. Sign and broadcast
counterparty-cli sign <unsigned_tx>
counterparty-cli broadcast <signed_tx>
```

## That's It! 🎉

Your audio is now inscribed on Bitcoin as a Counterparty token with Ordinals inscription format.
