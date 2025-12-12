"""
Tests for services module (log capture).
"""
import pytest
import sys
import logging
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.log_capture import LogCapture, LogCaptureHandler, get_log_capture


class TestLogCapture:
    """Test LogCapture class."""
    
    @pytest.fixture
    def log_capture(self):
        """Create LogCapture instance with small limits for testing."""
        return LogCapture(max_logs_per_request=10, max_requests=5)
    
    def test_initialization(self, log_capture):
        """Test LogCapture initialization."""
        assert log_capture is not None
        assert log_capture.max_logs_per_request == 10
        assert log_capture.max_requests == 5
        assert hasattr(log_capture, '_log_buffer')
        assert hasattr(log_capture, '_request_order')
    
    def test_add_log(self, log_capture):
        """Test adding log entries."""
        request_id = "test-request-1"
        log_capture.add_log(request_id, "INFO", "Test message")
        
        logs = log_capture.get_logs(request_id)
        assert len(logs) == 1
        assert "Test message" in logs[0]
        assert "INFO" in logs[0]
    
    def test_add_multiple_logs(self, log_capture):
        """Test adding multiple log entries for same request."""
        request_id = "test-request-1"
        
        for i in range(5):
            log_capture.add_log(request_id, "INFO", f"Message {i}")
        
        logs = log_capture.get_logs(request_id)
        assert len(logs) == 5
        assert all(f"Message {i}" in logs[i] for i in range(5))
    
    def test_add_logs_max_limit(self, log_capture):
        """Test log buffer respects max_logs_per_request limit."""
        request_id = "test-request-1"
        
        # Add more logs than max
        for i in range(15):
            log_capture.add_log(request_id, "INFO", f"Message {i}")
        
        logs = log_capture.get_logs(request_id)
        # Should only keep last 10 (max_logs_per_request)
        assert len(logs) == 10
        # Should have messages 5-14 (last 10)
        assert "Message 5" in logs[0]
        assert "Message 14" in logs[-1]
    
    def test_get_logs_nonexistent_request(self, log_capture):
        """Test getting logs for non-existent request."""
        logs = log_capture.get_logs("nonexistent-request")
        assert logs == []
    
    def test_get_logs_multiple_requests(self, log_capture):
        """Test getting logs for multiple different requests."""
        request_id_1 = "request-1"
        request_id_2 = "request-2"
        
        log_capture.add_log(request_id_1, "INFO", "Message 1")
        log_capture.add_log(request_id_2, "ERROR", "Message 2")
        log_capture.add_log(request_id_1, "WARNING", "Message 3")
        
        logs_1 = log_capture.get_logs(request_id_1)
        logs_2 = log_capture.get_logs(request_id_2)
        
        assert len(logs_1) == 2
        assert len(logs_2) == 1
        assert "Message 1" in logs_1[0]
        assert "Message 3" in logs_1[1]
        assert "Message 2" in logs_2[0]
    
    def test_get_last_n_logs(self, log_capture):
        """Test getting last N logs across all requests."""
        # Add logs for multiple requests
        for i in range(3):
            request_id = f"request-{i}"
            for j in range(3):
                log_capture.add_log(request_id, "INFO", f"Request {i} Message {j}")
        
        # Get last 5 logs
        last_logs = log_capture.get_last_n_logs(5)
        assert len(last_logs) == 5
        
        # Should have most recent logs
        assert "Request 2 Message 2" in last_logs[-1]
    
    def test_get_last_n_logs_less_than_total(self, log_capture):
        """Test getting last N logs when total is less than N."""
        request_id = "request-1"
        for i in range(3):
            log_capture.add_log(request_id, "INFO", f"Message {i}")
        
        last_logs = log_capture.get_last_n_logs(10)
        assert len(last_logs) == 3
    
    def test_get_last_n_logs_empty(self, log_capture):
        """Test getting last N logs when no logs exist."""
        last_logs = log_capture.get_last_n_logs(10)
        assert last_logs == []
    
    def test_max_requests_cleanup(self, log_capture):
        """Test cleanup of old requests when max_requests exceeded."""
        # Add requests up to max
        for i in range(5):
            request_id = f"request-{i}"
            log_capture.add_log(request_id, "INFO", f"Message {i}")
        
        # Add one more request (should trigger cleanup)
        log_capture.add_log("request-5", "INFO", "Message 5")
        
        # First request should be removed
        logs_0 = log_capture.get_logs("request-0")
        assert logs_0 == []
        
        # Latest request should exist
        logs_5 = log_capture.get_logs("request-5")
        assert len(logs_5) == 1
    
    def test_log_entry_format(self, log_capture):
        """Test log entry format includes timestamp and level."""
        request_id = "test-request"
        log_capture.add_log(request_id, "ERROR", "Test error message")
        
        logs = log_capture.get_logs(request_id)
        assert len(logs) == 1
        
        log_entry = logs[0]
        # Should contain timestamp, level, and message
        assert "ERROR" in log_entry
        assert "Test error message" in log_entry
        # Should have timestamp format YYYY-MM-DD HH:MM:SS
        assert "-" in log_entry  # Date separator
    
    def test_different_log_levels(self, log_capture):
        """Test different log levels."""
        request_id = "test-request"
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in levels:
            log_capture.add_log(request_id, level, f"{level} message")
        
        logs = log_capture.get_logs(request_id)
        assert len(logs) == len(levels)
        
        for level in levels:
            assert any(level in log for log in logs)


class TestLogCaptureHandler:
    """Test LogCaptureHandler class."""
    
    @pytest.fixture
    def handler(self):
        """Create LogCaptureHandler instance."""
        return LogCaptureHandler()
    
    @pytest.fixture
    def log_capture(self):
        """Create fresh LogCapture instance."""
        return LogCapture(max_logs_per_request=10, max_requests=5)
    
    def test_initialization(self, handler):
        """Test handler initialization."""
        assert handler is not None
        assert isinstance(handler, logging.Handler)
    
    def test_emit_with_request_id(self, handler, log_capture):
        """Test emit method captures logs with request_id."""
        # Patch the global log capture instance
        with patch('src.services.log_capture._log_capture', log_capture):
            # Create a mock log record with request_id
            record = Mock()
            record.request_id = "test-request-1"
            record.levelname = "INFO"
            record.getMessage.return_value = "Test log message"
            handler.format = Mock(return_value="2024-01-01 12:00:00 - INFO - Test log message")
            
            handler.emit(record)
            
            # Check that log was captured
            logs = log_capture.get_logs("test-request-1")
            assert len(logs) == 1
            assert "Test log message" in logs[0]
    
    def test_emit_without_request_id(self, handler, log_capture):
        """Test emit method ignores logs without request_id."""
        with patch('src.services.log_capture._log_capture', log_capture):
            # Create a mock log record without request_id
            record = Mock()
            record.request_id = None
            record.levelname = "INFO"
            handler.format = Mock(return_value="Test log message")
            
            handler.emit(record)
            
            # Should not capture (no request_id)
            # Verify by checking no logs were added
            assert len(log_capture._log_buffer) == 0
    
    def test_emit_exception_handling(self, handler):
        """Test emit method handles exceptions gracefully."""
        # Create a record that will cause an error
        record = Mock()
        record.request_id = "test-request"
        record.levelname = "INFO"
        
        # Make format raise an exception
        handler.format = Mock(side_effect=Exception("Format error"))
        
        # Should not raise exception (silently fails)
        try:
            handler.emit(record)
        except Exception:
            pytest.fail("emit() should handle exceptions gracefully")


class TestGetLogCapture:
    """Test get_log_capture function."""
    
    def test_get_log_capture_returns_instance(self):
        """Test get_log_capture returns LogCapture instance."""
        instance = get_log_capture()
        assert instance is not None
        assert isinstance(instance, LogCapture)
    
    def test_get_log_capture_singleton(self):
        """Test get_log_capture returns same instance."""
        instance1 = get_log_capture()
        instance2 = get_log_capture()
        assert instance1 is instance2

