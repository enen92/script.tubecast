# -*- coding: utf-8 -*-
import socket
import threading
import time
import unittest
from unittest.mock import MagicMock, patch

from resources.lib.service import run
from resources.lib.tubecast.ssdp import SSDPserver, MulticastServer


class TestIntegration(unittest.TestCase):
    """Integration tests for the service and SSDP components."""

    @patch('resources.lib.service.monitor')
    @patch('resources.lib.tubecast.ssdp.MulticastServer')
    @patch('resources.lib.tubecast.chromecast.make_server')
    def test_ssdp_retry_integration(self, mock_make_server, mock_multicast_server, mock_monitor):
        """Test that the service properly handles SSDP retry mechanism."""
        # Setup mocks
        mock_http_server = MagicMock()
        mock_make_server.return_value = mock_http_server
        mock_http_server.socket.getsockname.return_value = ('127.0.0.1', 8008)
        
        # Make MulticastServer fail initially then succeed on retry
        mock_multicast_server.side_effect = [
            socket.error("Network unavailable"),  # First attempt fails
            MagicMock()  # Second attempt succeeds
        ]
        
        # Mock the monitor to abort after a few iterations
        # First False to allow starting the server, then False to allow one loop iteration,
        # then True to exit the loop
        mock_monitor.abortRequested.side_effect = [False, False, True]
        
        # Replace the actual retry method with a faster version for testing
        original_retry_start = SSDPserver._retry_start
        
        def fast_retry(self, *args, **kwargs):
            # Override retry_delay to make tests run faster
            return original_retry_start(self, *args, retry_delay=0.1, **kwargs)
        
        # Apply the patch
        with patch.object(SSDPserver, '_retry_start', fast_retry):
            # Run the service - should start Chromecast, fail to start SSDP initially,
            # then start retry thread, then succeed on retry
            run()
            
            # Verify that the SSDP server was eventually called successfully
            assert mock_multicast_server.call_count == 2
    
    @patch('resources.lib.service.monitor')
    @patch('resources.lib.tubecast.ssdp.MulticastServer')
    @patch('resources.lib.tubecast.chromecast.make_server')
    def test_ssdp_retry_with_eventual_failure(self, mock_make_server, mock_multicast_server, mock_monitor):
        """Test that the service continues to work even if SSDP never succeeds."""
        # Setup mocks
        mock_http_server = MagicMock()
        mock_make_server.return_value = mock_http_server
        mock_http_server.socket.getsockname.return_value = ('127.0.0.1', 8008)
        
        # Make MulticastServer always fail
        mock_multicast_server.side_effect = socket.error("Network permanently unavailable")
        
        # Mock the monitor to abort after a few iterations
        mock_monitor.abortRequested.side_effect = [False, False, True]
        
        # Run the service - should start Chromecast, fail to start SSDP,
        # start retry thread, and exit without crashing
        run()
        
        # Verify that at least one attempt was made
        assert mock_multicast_server.call_count >= 1


if __name__ == '__main__':
    unittest.main() 