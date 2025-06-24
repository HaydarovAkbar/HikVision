import unittest
import sys
import os

# Loyiha yo'lini qo'shish
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import HikVisionConfig
from src.hikvision_api import HikVisionAPI
from src.parser import HikVisionParser

class TestHikVisionAPI(unittest.TestCase):
    """HikVision API testlari"""
    
    def setUp(self):
        """Test uchun sozlash"""
        self.config = HikVisionConfig()
        self.api = HikVisionAPI(self.config)
        self.parser = HikVisionParser(self.api)
    
    def test_config_loading(self):
        """Konfiguratsiya yuklashni test qilish"""
        self.assertIsNotNone(self.config.HOST)
        self.assertIsNotNone(self.config.USERNAME)
        self.assertIsNotNone(self.config.PASSWORD)
        self.assertEqual(self.config.HOST, "172.18.18.60")
    
    def test_api_initialization(self):
        """API ishga tushirishni test qilish"""
        self.assertIsNotNone(self.api.config)
        self.assertIsNotNone(self.api.session)
        self.assertEqual(self.api.config.HOST, "172.18.18.60")
    
    def test_base_url_generation(self):
        """Base URL yaratishni test qilish"""
        expected_url = "http://172.18.18.60:80"
        self.assertEqual(self.config.base_url, expected_url)
    
    def test_api_url_generation(self):
        """API URL yaratishni test qilish"""
        endpoint = "ISAPI/System/deviceInfo"
        expected_url = f"{self.config.base_url}/{endpoint}"
        actual_url = self.config.get_api_url(endpoint)
        self.assertEqual(actual_url, expected_url)
    
    def test_parser_initialization(self):
        """Parser ishga tushirishni test qilish"""
        self.assertIsNotNone(self.parser.api)
    
    def test_xml_to_dict_simple(self):
        """Oddiy XML dan dict ga aylantirish testi"""
        import xml.etree.ElementTree as ET
        xml_string = "<root><name>test</name><value>123</value></root>"
        root = ET.fromstring(xml_string)
        result = self.api._xml_to_dict(root)
        
        self.assertIn('name', result)
        self.assertIn('value', result)
        self.assertEqual(result['name'], 'test')
        self.assertEqual(result['value'], '123')
    
    def test_connection_timeout(self):
        """Ulanish timeout ni test qilish"""
        self.assertEqual(self.api.session.timeout, self.config.TIMEOUT)
    
    def test_authentication_setup(self):
        """Autentifikatsiya sozlashni test qilish"""
        from requests.auth import HTTPDigestAuth
        self.assertIsInstance(self.api.session.auth, HTTPDigestAuth)

class TestHikVisionParser(unittest.TestCase):
    """HikVision Parser testlari"""
    
    def setUp(self):
        """Test uchun sozlash"""
        self.parser = HikVisionParser()
    
    def test_parse_device_info(self):
        """Qurilma ma'lumotlarini parsing testi"""
        sample_device_info = {
            'DeviceInfo': {
                'deviceName': 'Test Camera',
                'deviceID': '123456',
                'model': 'DS-2CD2086G2-I',
                'serialNumber': 'ABC123',
                'firmwareVersion': 'V5.7.0',
                'macAddress': '00:11:22:33:44:55',
                'ipAddress': '192.168.1.100'
            }
        }
        
        result = self.parser.parse_device_info(sample_device_info)
        
        self.assertEqual(result['device_name'], 'Test Camera')
        self.assertEqual(result['device_id'], '123456')
        self.assertEqual(result['model'], 'DS-2CD2086G2-I')
        self.assertEqual(result['serial_number'], 'ABC123')
        self.assertIn('timestamp', result)
    
    def test_parse_channels(self):
        """Kanallarni parsing testi"""
        sample_channels = [
            {
                'id': '1',
                'channelName': 'Camera 1',
                'enabled': 'true',
                'inputPort': '1',
                'videoFormat': 'PAL',
                'resolutionHeight': '1080',
                'resolutionWidth': '1920'
            }
        ]
        
        result = self.parser.parse_channels(sample_channels)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['channel_id'], '1')
        self.assertEqual(result[0]['channel_name'], 'Camera 1')
        self.assertTrue(result[0]['enabled'])
        self.assertEqual(result[0]['resolution_height'], 1080)

if __name__ == '__main__':
    # Test ishga tushirish
    print("HikVision API testlari ishga tushmoqda...")
    unittest.main(verbosity=2)
