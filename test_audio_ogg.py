#!/usr/bin/env python3
"""
Test script to verify audio/ogg;codecs=opus MIME type support
"""

import sys
import os

# Add the counterparty-core directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'counterparty-core'))

from counterpartycore.lib.utils import helpers
import mimetypes


def test_mime_type_registration():
    """Test that custom MIME types are registered"""
    print("Testing MIME type registration...")
    
    # Check if audio/ogg is registered
    assert 'audio/ogg' in mimetypes.types_map.values(), "audio/ogg should be registered"
    print("✓ audio/ogg is registered")
    
    # Check if video/ogg is registered
    assert 'video/ogg' in mimetypes.types_map.values(), "video/ogg should be registered"
    print("✓ video/ogg is registered")
    
    print()


def test_parse_mime_type():
    """Test MIME type parsing with codec parameters"""
    print("Testing MIME type parsing...")
    
    # Test simple MIME type
    base, params = helpers.parse_mime_type("audio/ogg")
    assert base == "audio/ogg", f"Expected 'audio/ogg', got '{base}'"
    assert params == {}, f"Expected empty params, got {params}"
    print("✓ Simple MIME type: audio/ogg")
    
    # Test MIME type with codec parameter
    base, params = helpers.parse_mime_type("audio/ogg;codecs=opus")
    assert base == "audio/ogg", f"Expected 'audio/ogg', got '{base}'"
    assert params == {"codecs": "opus"}, f"Expected {{'codecs': 'opus'}}, got {params}"
    print("✓ MIME type with codec: audio/ogg;codecs=opus")
    
    # Test MIME type with multiple parameters
    base, params = helpers.parse_mime_type("audio/ogg;codecs=opus;rate=48000")
    assert base == "audio/ogg", f"Expected 'audio/ogg', got '{base}'"
    assert params == {"codecs": "opus", "rate": "48000"}, f"Expected codec and rate params, got {params}"
    print("✓ MIME type with multiple params: audio/ogg;codecs=opus;rate=48000")
    
    # Test empty MIME type
    base, params = helpers.parse_mime_type("")
    assert base == "", f"Expected empty string, got '{base}'"
    assert params == {}, f"Expected empty params, got {params}"
    print("✓ Empty MIME type handled correctly")
    
    print()


def test_check_content():
    """Test content validation with various MIME types"""
    print("Testing content validation...")
    
    # Test audio/ogg (simple)
    problems = helpers.check_content("audio/ogg", "deadbeef")
    assert len(problems) == 0, f"audio/ogg should be valid, got problems: {problems}"
    print("✓ audio/ogg is valid")
    
    # Test audio/ogg;codecs=opus
    problems = helpers.check_content("audio/ogg;codecs=opus", "deadbeef")
    assert len(problems) == 0, f"audio/ogg;codecs=opus should be valid, got problems: {problems}"
    print("✓ audio/ogg;codecs=opus is valid")
    
    # Test audio/ogg;codecs=vorbis
    problems = helpers.check_content("audio/ogg;codecs=vorbis", "deadbeef")
    assert len(problems) == 0, f"audio/ogg;codecs=vorbis should be valid, got problems: {problems}"
    print("✓ audio/ogg;codecs=vorbis is valid")
    
    # Test existing MIME types still work
    problems = helpers.check_content("text/plain", "Hello World")
    assert len(problems) == 0, f"text/plain should be valid, got problems: {problems}"
    print("✓ text/plain still works (backward compatibility)")
    
    problems = helpers.check_content("image/png", "89504e47")
    assert len(problems) == 0, f"image/png should be valid, got problems: {problems}"
    print("✓ image/png still works (backward compatibility)")
    
    # Test invalid MIME type
    problems = helpers.check_content("invalid/mimetype", "data")
    assert len(problems) > 0, "invalid/mimetype should produce problems"
    print("✓ Invalid MIME types are still rejected")
    
    print()


def test_classify_mime_type():
    """Test that audio types are classified as binary"""
    print("Testing MIME type classification...")
    
    file_type = helpers.classify_mime_type("audio/ogg")
    assert file_type == "binary", f"audio/ogg should be binary, got '{file_type}'"
    print("✓ audio/ogg classified as binary")
    
    file_type = helpers.classify_mime_type("audio/opus")
    assert file_type == "binary", f"audio/opus should be binary, got '{file_type}'"
    print("✓ audio/opus classified as binary")
    
    file_type = helpers.classify_mime_type("text/plain")
    assert file_type == "text", f"text/plain should be text, got '{file_type}'"
    print("✓ text/plain classified as text")
    
    print()


def test_content_conversion():
    """Test content to bytes conversion"""
    print("Testing content conversion...")
    
    # Test binary content (hex string)
    hex_data = "deadbeef"
    result = helpers.content_to_bytes(hex_data, "audio/ogg")
    expected = bytes.fromhex(hex_data)
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ Binary content conversion works for audio/ogg")
    
    # Test text content
    text_data = "Hello World"
    result = helpers.content_to_bytes(text_data, "text/plain")
    expected = text_data.encode("utf-8")
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ Text content conversion still works")
    
    print()


def main():
    """Run all tests"""
    print("=" * 60)
    print("Audio/OGG Opus MIME Type Support Test")
    print("=" * 60)
    print()
    
    try:
        test_mime_type_registration()
        test_parse_mime_type()
        test_check_content()
        test_classify_mime_type()
        test_content_conversion()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("Summary:")
        print("- audio/ogg MIME type is now registered")
        print("- audio/ogg;codecs=opus is supported")
        print("- Codec parameters are properly parsed")
        print("- Backward compatibility maintained")
        return 0
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print("❌ TEST FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ UNEXPECTED ERROR!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
