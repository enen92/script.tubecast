# -*- coding: utf-8 -*-
import socket
import threading
import time
import unittest
from unittest.mock import MagicMock, patch

import pytest

from resources.lib.tubecast.ssdp import SSDPserver


class TestSSDPResilience(unittest.TestCase):
    """Test cases for the SSDP server's resilience to network issues."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the logger to avoid actual logging during tests
        self.logger_patcher = patch('resources.lib.tubecast.ssdp.logger')
        self.mock_logger = self.logger_patcher.start()
        
        # Mock chromecast address
        self.mock_chromecast_addr = ('127.0.0.1', 8008)

    def tearDown(self):
        """Tear down test fixtures."""
        self.logger_patcher.stop()

    @patch('resources.lib.tubecast.ssdp.MulticastServer')
    def test_start_server_success(self, mock_multicast_server):
        """Test that the SSDP server starts successfully when no errors occur."""
        # Arrange
        ssdp_server = SSDPserver()
        mock_server_instance = mock_multicast_server.return_value
        
        # Act
        ssdp_server.start(self.mock_chromecast_addr)
        
        # Assert
        mock_multicast_server.assert_called_once_with(
            (ssdp_server.SSDP_ADDR, ssdp_server.SSDP_PORT),
            unittest.mock.ANY,  # SSDPHandler
            chromecast_addr=self.mock_chromecast_addr,
            interfaces=None
        )
        mock_server_instance.start.assert_called_once()
        assert ssdp_server.is_running is True
        assert ssdp_server.server is mock_server_instance
        self.mock_logger.info.assert_called_with('Starting SSDP server')

    @patch('resources.lib.tubecast.ssdp.MulticastServer')
    def test_start_server_socket_error(self, mock_multicast_server):
        """Test that the SSDP server handles socket errors gracefully."""
        # Arrange
        ssdp_server = SSDPserver()
        mock_multicast_server.side_effect = socket.error("Network unavailable")
        
        # Act
        ssdp_server.start(self.mock_chromecast_addr)
        
        # Assert
        assert ssdp_server.is_running is False
        assert ssdp_server.server is None
        assert ssdp_server.retry_thread is not None
        assert ssdp_server.retry_thread.is_alive()
        self.mock_logger.warning.assert_called_once()

    @patch('resources.lib.tubecast.ssdp.MulticastServer')
    def test_start_server_os_error(self, mock_multicast_server):
        """Test that the SSDP server handles OS errors gracefully."""
        # Arrange
        ssdp_server = SSDPserver()
        mock_multicast_server.side_effect = OSError("Permission denied")
        
        # Act
        ssdp_server.start(self.mock_chromecast_addr)
        
        # Assert
        assert ssdp_server.is_running is False
        assert ssdp_server.server is None
        assert ssdp_server.retry_thread is not None
        assert ssdp_server.retry_thread.is_alive()
        self.mock_logger.warning.assert_called_once()

    @patch('resources.lib.tubecast.ssdp.MulticastServer')
    def test_retry_mechanism(self, mock_multicast_server):
        """Test that the retry mechanism correctly attempts to restart the server."""
        # Arrange
        ssdp_server = SSDPserver()
        
        # Make the first attempt fail but second succeed
        mock_multicast_server.side_effect = [
            socket.error("Network unavailable"),  # First call fails
            MagicMock()  # Second call succeeds
        ]
        
        # Act
        ssdp_server.start(self.mock_chromecast_addr)
        
        # Wait for retry - we'll override the retry delay to make test faster
        with patch.object(ssdp_server, '_retry_start') as mock_retry:
            # Extract the retry args
            args, kwargs = mock_retry.call_args
            # Call the retry directly with minimal delay
            ssdp_server._retry_start(*args, retry_delay=0.1)
            
            # Sleep briefly to allow the retry logic to execute
            time.sleep(0.2)
            
            # Assert
            assert ssdp_server.is_running is True
            assert ssdp_server.server is not None
            mock_multicast_server.call_count == 2

    @patch('resources.lib.tubecast.ssdp.MulticastServer')
    def test_shutdown_with_no_server(self, mock_multicast_server):
        """Test that shutdown handles the case when no server was started."""
        # Arrange
        ssdp_server = SSDPserver()
        
        # Act - shutdown without starting
        ssdp_server.shutdown()
        
        # Assert - should not raise exceptions
        assert ssdp_server.is_running is False
        assert ssdp_server.server is None

    @patch('resources.lib.tubecast.ssdp.MulticastServer')
    def test_shutdown_with_retry_thread(self, mock_multicast_server):
        """Test that shutdown properly stops the retry thread."""
        # Arrange
        ssdp_server = SSDPserver()
        mock_multicast_server.side_effect = socket.error("Network unavailable")
        
        # Start server, which should fail and start retry thread
        ssdp_server.start(self.mock_chromecast_addr)
        assert ssdp_server.retry_thread is not None
        assert ssdp_server.retry_thread.is_alive()
        
        # Act
        ssdp_server.shutdown()
        
        # Assert
        assert ssdp_server.stop_retry.is_set()  # Signal to stop retry thread
        # In a real scenario, the thread would stop soon after

    @patch('resources.lib.tubecast.ssdp.MulticastServer')
    def test_shutdown_with_server(self, mock_multicast_server):
        """Test that shutdown properly stops the server if it was running."""
        # Arrange
        ssdp_server = SSDPserver()
        mock_server = MagicMock()
        mock_multicast_server.return_value = mock_server
        
        # Start the server successfully
        ssdp_server.start(self.mock_chromecast_addr)
        assert ssdp_server.is_running is True
        
        # Act
        ssdp_server.shutdown()
        
        # Assert
        mock_server.server_close.assert_called_once()
        mock_server.stop.assert_called_once()
        assert ssdp_server.is_running is False
        assert ssdp_server.server is None

    @patch('resources.lib.tubecast.ssdp.MulticastServer')
    def test_shutdown_handles_errors(self, mock_multicast_server):
        """Test that shutdown handles errors that might occur during server close."""
        # Arrange
        ssdp_server = SSDPserver()
        mock_server = MagicMock()
        mock_server.server_close.side_effect = Exception("Error during close")
        mock_multicast_server.return_value = mock_server
        
        # Start the server successfully
        ssdp_server.start(self.mock_chromecast_addr)
        
        # Act
        ssdp_server.shutdown()
        
        # Assert
        self.mock_logger.error.assert_called_once()
        assert ssdp_server.is_running is False
        assert ssdp_server.server is None

    @patch('resources.lib.tubecast.ssdp.MulticastServer')
    def test_multiple_start_attempts_with_eventual_success(self, mock_multicast_server):
        """Test that multiple failed start attempts followed by success work correctly."""
        # Arrange
        ssdp_server = SSDPserver()
        
        # Configure mock to fail three times then succeed
        mock_multicast_server.side_effect = [
            socket.error("Network unavailable"),  # First call fails
            socket.error("Network unavailable"),  # Second call fails
            socket.error("Network unavailable"),  # Third call fails
            MagicMock()  # Fourth call succeeds
        ]
        
        # Mock the retry delay to make the test faster
        original_retry_start = ssdp_server._retry_start
        
        def mock_retry_with_fast_delay(*args, **kwargs):
            # Override the retry_delay parameter
            return original_retry_start(*args, retry_delay=0.1)
        
        # Replace the method with our mocked version
        ssdp_server._retry_start = mock_retry_with_fast_delay
        
        # Act
        ssdp_server.start(self.mock_chromecast_addr)
        
        # Let the retry mechanism run a few times
        retry_attempts = 0
        max_wait_time = 2  # seconds
        start_time = time.time()
        
        while (not ssdp_server.is_running and 
               time.time() - start_time < max_wait_time and 
               retry_attempts < 5):
            time.sleep(0.2)
            retry_attempts += 1
        
        # Assert
        assert ssdp_server.is_running is True
        assert ssdp_server.server is not None
        assert mock_multicast_server.call_count >= 4 