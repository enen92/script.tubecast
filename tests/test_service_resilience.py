# -*- coding: utf-8 -*-
import unittest
from unittest.mock import MagicMock, patch

from resources.lib.service import run


class TestServiceResilience(unittest.TestCase):
    """Test cases for the service module's resilience to network issues."""

    @patch('resources.lib.service.SSDPserver')
    @patch('resources.lib.service.Chromecast')
    @patch('resources.lib.service.generate_uuid')
    @patch('resources.lib.service.get_setting_as_bool')
    @patch('resources.lib.service.monitor')
    @patch('resources.lib.service.logger')
    def test_service_handles_ssdp_exception(self, mock_logger, mock_monitor, 
                                           mock_get_setting, mock_generate_uuid, 
                                           mock_chromecast, mock_ssdp_server):
        """Test that the service handles exceptions from SSDP server."""
        # Arrange
        mock_get_setting.return_value = True  # Enable SSDP
        mock_chromecast_instance = MagicMock()
        mock_chromecast.return_value = mock_chromecast_instance
        mock_chromecast_instance.start.return_value = ('127.0.0.1', 8008)
        
        # Mock the SSDPserver to raise an exception during start
        mock_ssdp_instance = MagicMock()
        mock_ssdp_server.return_value = mock_ssdp_instance
        mock_ssdp_instance.start.side_effect = Exception("SSDP server error")
        
        # Make monitor.abortRequested return True after first check to exit the loop
        mock_monitor.abortRequested.side_effect = [False, True]
        
        # Act
        run()
        
        # Assert
        mock_generate_uuid.assert_called_once()
        mock_chromecast.assert_called_once()
        mock_chromecast_instance.start.assert_called_once()
        mock_ssdp_server.assert_called_once()
        mock_ssdp_instance.start.assert_called_once()
        mock_logger.error.assert_called_once()
        # Verify that chromecast.abort is called during shutdown
        mock_chromecast_instance.abort.assert_called_once()

    @patch('resources.lib.service.SSDPserver')
    @patch('resources.lib.service.Chromecast')
    @patch('resources.lib.service.generate_uuid')
    @patch('resources.lib.service.get_setting_as_bool')
    @patch('resources.lib.service.monitor')
    def test_service_with_ssdp_disabled(self, mock_monitor, mock_get_setting, 
                                       mock_generate_uuid, mock_chromecast, 
                                       mock_ssdp_server):
        """Test that the service doesn't start SSDP if it's disabled."""
        # Arrange
        mock_get_setting.return_value = False  # Disable SSDP
        mock_chromecast_instance = MagicMock()
        mock_chromecast.return_value = mock_chromecast_instance
        mock_chromecast_instance.start.return_value = ('127.0.0.1', 8008)
        
        # Make monitor.abortRequested return True after first check to exit the loop
        mock_monitor.abortRequested.side_effect = [False, True]
        
        # Act
        run()
        
        # Assert
        mock_generate_uuid.assert_called_once()
        mock_chromecast.assert_called_once()
        mock_chromecast_instance.start.assert_called_once()
        mock_ssdp_server.assert_not_called()  # SSDP server should not be instantiated
        mock_chromecast_instance.abort.assert_called_once()

    @patch('resources.lib.service.SSDPserver')
    @patch('resources.lib.service.Chromecast')
    @patch('resources.lib.service.generate_uuid')
    @patch('resources.lib.service.get_setting_as_bool')
    @patch('resources.lib.service.monitor')
    def test_service_shuts_down_ssdp_if_running(self, mock_monitor, mock_get_setting, 
                                              mock_generate_uuid, mock_chromecast, 
                                              mock_ssdp_server):
        """Test that the service shuts down SSDP if it was started."""
        # Arrange
        mock_get_setting.return_value = True  # Enable SSDP
        mock_chromecast_instance = MagicMock()
        mock_chromecast.return_value = mock_chromecast_instance
        mock_chromecast_instance.start.return_value = ('127.0.0.1', 8008)
        
        mock_ssdp_instance = MagicMock()
        mock_ssdp_server.return_value = mock_ssdp_instance
        
        # Make monitor.abortRequested return True after first check to exit the loop
        mock_monitor.abortRequested.side_effect = [False, True]
        
        # Act
        run()
        
        # Assert
        mock_generate_uuid.assert_called_once()
        mock_chromecast.assert_called_once()
        mock_chromecast_instance.start.assert_called_once()
        mock_ssdp_server.assert_called_once()
        mock_ssdp_instance.start.assert_called_once()
        # Verify that both ssdp.shutdown and chromecast.abort are called during shutdown
        mock_ssdp_instance.shutdown.assert_called_once()
        mock_chromecast_instance.abort.assert_called_once()

    @patch('resources.lib.service.SSDPserver')
    @patch('resources.lib.service.Chromecast')
    @patch('resources.lib.service.generate_uuid')
    @patch('resources.lib.service.get_setting_as_bool')
    @patch('resources.lib.service.monitor')
    @patch('resources.lib.service.logger')
    def test_service_handles_shutdown_exception(self, mock_logger, mock_monitor, 
                                              mock_get_setting, mock_generate_uuid, 
                                              mock_chromecast, mock_ssdp_server):
        """Test that the service handles exceptions during shutdown."""
        # Arrange
        mock_get_setting.return_value = True  # Enable SSDP
        mock_chromecast_instance = MagicMock()
        mock_chromecast.return_value = mock_chromecast_instance
        mock_chromecast_instance.start.return_value = ('127.0.0.1', 8008)
        mock_chromecast_instance.abort.side_effect = Exception("Chromecast abort error")
        
        mock_ssdp_instance = MagicMock()
        mock_ssdp_server.return_value = mock_ssdp_instance
        mock_ssdp_instance.shutdown.side_effect = Exception("SSDP shutdown error")
        
        # Make monitor.abortRequested return True after first check to exit the loop
        mock_monitor.abortRequested.side_effect = [False, True]
        
        # Act - this should not raise exceptions even though both shutdown calls fail
        run()
        
        # Assert
        mock_generate_uuid.assert_called_once()
        mock_chromecast.assert_called_once()
        mock_chromecast_instance.start.assert_called_once()
        mock_ssdp_server.assert_called_once()
        mock_ssdp_instance.start.assert_called_once()
        mock_ssdp_instance.shutdown.assert_called_once()
        mock_chromecast_instance.abort.assert_called_once()
        # Two errors should be logged for the two shutdown failures
        assert mock_logger.error.call_count >= 2 