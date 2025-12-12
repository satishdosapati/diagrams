"""
Log capture service for error reporting.
Maintains in-memory buffer of log entries per request ID.
"""
import logging
from typing import List, Dict, Optional
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)


class LogCapture:
    """
    In-memory log buffer for capturing logs per request ID.
    Stores last N log entries per request for error reporting.
    """
    
    def __init__(self, max_logs_per_request: int = 50, max_requests: int = 1000):
        """
        Initialize log capture.
        
        Args:
            max_logs_per_request: Maximum log entries to store per request
            max_requests: Maximum number of requests to track
        """
        self.max_logs_per_request = max_logs_per_request
        self.max_requests = max_requests
        # Format: {request_id: deque([log_entry, ...])}
        self._log_buffer: Dict[str, deque] = {}
        # Track request order for cleanup
        self._request_order: deque = deque(maxlen=max_requests)
    
    def add_log(self, request_id: str, level: str, message: str):
        """
        Add a log entry for a request.
        
        Args:
            request_id: Request identifier
            level: Log level (INFO, ERROR, WARNING, etc.)
            message: Log message
        """
        if request_id not in self._log_buffer:
            # Initialize deque for this request
            self._log_buffer[request_id] = deque(maxlen=self.max_logs_per_request)
            self._request_order.append(request_id)
            
            # Cleanup old requests if we exceed max
            if len(self._log_buffer) > self.max_requests:
                oldest_request = self._request_order.popleft()
                if oldest_request in self._log_buffer:
                    del self._log_buffer[oldest_request]
        
        # Format log entry
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} - {level} - {message}"
        
        # Add to buffer
        self._log_buffer[request_id].append(log_entry)
    
    def get_logs(self, request_id: str) -> List[str]:
        """
        Get logs for a request ID.
        
        Args:
            request_id: Request identifier
            
        Returns:
            List of log entries (last N lines)
        """
        if request_id not in self._log_buffer:
            return []
        
        return list(self._log_buffer[request_id])
    
    def get_last_n_logs(self, n: int = 50) -> List[str]:
        """
        Get last N log entries across all requests (fallback).
        
        Args:
            n: Number of log entries to return
            
        Returns:
            List of log entries
        """
        all_logs = []
        for request_id in reversed(list(self._request_order)):
            if request_id in self._log_buffer:
                all_logs.extend(self._log_buffer[request_id])
                if len(all_logs) >= n:
                    return all_logs[-n:]
        
        return all_logs


# Global instance
_log_capture = LogCapture()


def get_log_capture() -> LogCapture:
    """Get the global log capture instance."""
    return _log_capture


# Custom logging handler to capture logs
class LogCaptureHandler(logging.Handler):
    """Logging handler that captures logs to in-memory buffer."""
    
    def emit(self, record):
        """Emit a log record."""
        try:
            # Extract request_id from log record if available
            # The request_id is set by the logging factory in middleware
            request_id = getattr(record, 'request_id', None)
            if request_id:
                # Format the log message (includes timestamp, logger name, level, message)
                message = self.format(record)
                _log_capture.add_log(request_id, record.levelname, message)
        except Exception as e:
            # Don't let logging errors break the app
            # Silently fail to avoid infinite recursion if logging itself fails
            pass

