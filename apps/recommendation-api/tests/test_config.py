"""Tests for configuration module."""

import pytest
from recommendation_api.config import Config, get_config, reset_config


def test_config_creation():
    """Test that Config can be created with defaults."""
    config = Config()
    
    ***REMOVED*** Test basic attributes exist
    assert hasattr(config, 'database_url')
    assert hasattr(config, 'qdrant_url')
    assert hasattr(config, 'embedding_model')
    assert hasattr(config, 'port')
    assert hasattr(config, 'debug')
    
    ***REMOVED*** Test default values
    assert config.port == 8004
    assert config.embedding_dimension == 384
    assert config.batch_size == 100


def test_config_singleton():
    """Test that get_config returns the same instance."""
    reset_config()  ***REMOVED*** Reset for clean test
    
    config1 = get_config()
    config2 = get_config()
    
    assert config1 is config2


def test_config_repr():
    """Test that config string representation masks sensitive data."""
    config = Config()
    repr_str = repr(config)
    
    assert "***masked***" in repr_str
    assert config.qdrant_url in repr_str
    assert config.embedding_model in repr_str


def test_config_mask_database_password():
    """Test database password masking."""
    config = Config()
    
    ***REMOVED*** Test with password in URL
    test_url = "postgresql://user:password@localhost:5432/db"
    masked = config._mask_database_password(test_url)
    
    assert "password" not in masked
    assert "****" in masked
    assert "user" in masked
    assert "localhost" in masked
    
    ***REMOVED*** Test with URL without password
    simple_url = "postgresql://localhost:5432/db"
    masked_simple = config._mask_database_password(simple_url)
    
    assert masked_simple == simple_url  ***REMOVED*** Should be unchanged


def test_config_environment_detection():
    """Test environment detection."""
    config = Config()
    
    ***REMOVED*** Should have environment attribute
    assert hasattr(config, 'environment')
    assert hasattr(config, 'is_production')
    
    ***REMOVED*** Default should be development
    assert config.environment in ['development', 'production'] 