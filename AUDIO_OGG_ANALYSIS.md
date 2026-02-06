# Audio/OGG Opus Support Analysis

## Current State

This fork of counterparty-core aims to support `audio/ogg;codecs=opus` MIME type for inscriptions when creating Counterparty tokens.

## Problem Identified

The current implementation validates MIME types using Python's built-in `mimetypes` module in `helpers.py`:

```python
def check_content(mime_type, content):
    problems = []
    content_mime_type = mime_type or "text/plain"
    if content_mime_type not in mimetypes.types_map.values():
        problems.append(f"Invalid mime type: {mime_type}")
    # ...
```

### Issues:
1. **`audio/ogg` is not in Python's mimetypes.types_map** - Python's standard library doesn't include `audio/ogg` by default
2. **Codec parameters not supported** - The format `audio/ogg;codecs=opus` includes codec parameters (`;codecs=opus`) which is valid per RFC 6381 but not handled by the simple validation
3. **Python has `audio/opus`** - Python's mimetypes includes `audio/opus` for `.opus` files, but not `audio/ogg`

## Current MIME Type Validation Flow

1. **Location**: `/counterparty-core/counterpartycore/lib/utils/helpers.py`
2. **Function**: `check_content(mime_type, content)`
3. **Validation**: Checks if `mime_type` exists in `mimetypes.types_map.values()`
4. **Used by**: 
   - `issuance.py` - for token issuance with inscriptions
   - `fairminter.py` - for fair minting with inscriptions
   - `broadcast.py` - for broadcasts with inscriptions

## Inscription Flow

When `inscription=True` is set in construct_params:

1. **composer.py** `generate_envelope_script()` is called
2. For supported message types (issuance, fairminter, broadcast), it calls `generate_ordinal_envelope_script()`
3. The envelope script includes:
   - Ordinals envelope format (`OP_FALSE OP_IF "ord" ...`)
   - XCP protocol marker
   - MIME type
   - Metadata (CBOR encoded)
   - Content chunks

## Solution Required

To support `audio/ogg;codecs=opus`, we need to:

### 1. Add Custom MIME Types
Register `audio/ogg` and related types in the mimetypes module at initialization.

### 2. Handle Codec Parameters
Parse and validate MIME types with codec parameters (e.g., `audio/ogg;codecs=opus`).

### 3. Update Validation Logic
Modify `check_content()` to:
- Strip codec parameters before validation
- Support custom audio MIME types
- Maintain backward compatibility

## Recommended Implementation

### File: `counterpartycore/lib/utils/helpers.py`

Add initialization code to register custom MIME types and update validation:

```python
# At module initialization
def _init_custom_mimetypes():
    """Register custom MIME types not in Python's standard library"""
    mimetypes.add_type('audio/ogg', '.ogg')
    mimetypes.add_type('audio/ogg', '.oga')
    mimetypes.add_type('video/ogg', '.ogv')
    mimetypes.add_type('application/ogg', '.ogx')

_init_custom_mimetypes()

def parse_mime_type(mime_type: str) -> tuple[str, dict]:
    """
    Parse MIME type with optional parameters.
    Returns (base_type, parameters_dict)
    
    Example: 'audio/ogg;codecs=opus' -> ('audio/ogg', {'codecs': 'opus'})
    """
    parts = mime_type.split(';')
    base_type = parts[0].strip()
    params = {}
    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=', 1)
            params[key.strip()] = value.strip()
    return base_type, params

def check_content(mime_type, content):
    problems = []
    content_mime_type = mime_type or "text/plain"
    
    # Parse MIME type to handle codec parameters
    base_mime_type, params = parse_mime_type(content_mime_type)
    
    # Validate base MIME type
    if base_mime_type not in mimetypes.types_map.values():
        problems.append(f"Invalid mime type: {mime_type}")
    
    try:
        content_to_bytes(content, base_mime_type)
    except Exception as e:
        problems.append(f"Error converting description to bytes: {e}")
    
    return problems
```

## Testing

Create test cases for:
1. `audio/ogg` - basic OGG audio
2. `audio/ogg;codecs=opus` - OGG with Opus codec
3. `audio/ogg;codecs=vorbis` - OGG with Vorbis codec
4. Backward compatibility with existing MIME types

## Files to Modify

1. `/counterparty-core/counterpartycore/lib/utils/helpers.py` - Add MIME type registration and parsing
2. Add integration tests in `/counterparty-core/counterpartycore/test/integrations/regtest/`

## Notes

- The `classify_mime_type()` function already correctly classifies audio types as "binary"
- The `content_to_bytes()` and `bytes_to_content()` functions will work correctly for audio files
- The inscription envelope script generation in `composer.py` doesn't need changes
