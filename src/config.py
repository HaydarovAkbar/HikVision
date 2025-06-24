import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv('config/settings.env')

class HikVisionConfig:
    """HikVision konfiguratsiya sinfi - Access Control uchun moslashtirilgan"""
    
    # Server ma'lumotlari
    HOST = os.getenv('HIKVISION_HOST', '172.18.18.60')
    USERNAME = os.getenv('HIKVISION_USERNAME', 'admin')
    PASSWORD = os.getenv('HIKVISION_PASSWORD', 'qwerty@321')
    PORT = int(os.getenv('HIKVISION_PORT', 80))
    PROTOCOL = os.getenv('HIKVISION_PROTOCOL', 'http')
    
    # Access Control API yo'llari
    API_DEVICE_INFO = os.getenv('API_DEVICE_INFO', 'ISAPI/System/deviceInfo')
    API_ACCESS_CONTROL = os.getenv('API_ACCESS_CONTROL', 'ISAPI/AccessControl/AcsEvent')
    API_CARD_INFO = os.getenv('API_CARD_INFO', 'ISAPI/AccessControl/CardInfo')
    API_USER_INFO = os.getenv('API_USER_INFO', 'ISAPI/AccessControl/UserInfo')
    API_DOOR_STATUS = os.getenv('API_DOOR_STATUS', 'ISAPI/AccessControl/Door')
    API_DOOR_CONTROL = os.getenv('API_DOOR_CONTROL', 'ISAPI/AccessControl/RemoteControl/door')
    API_EVENT_NOTIFICATION = os.getenv('API_EVENT_NOTIFICATION', 'ISAPI/Event/notification/alertStream')
    API_TIME_CONFIG = os.getenv('API_TIME_CONFIG', 'ISAPI/System/time')
    API_NETWORK_CONFIG = os.getenv('API_NETWORK_CONFIG', 'ISAPI/System/Network/interfaces')
    API_CAPABILITIES = os.getenv('API_CAPABILITIES', 'ISAPI/System/capabilities')
    
    # Eski kamera API lari (agar kerak bo'lsa)
    API_CHANNELS = os.getenv('API_CHANNELS', 'ISAPI/System/Video/inputs')
    API_STREAMING = os.getenv('API_STREAMING', 'ISAPI/Streaming/channels')
    API_PTZ = os.getenv('API_PTZ', 'ISAPI/PTZCtrl/channels')
    API_PLAYBACK = os.getenv('API_PLAYBACK', 'ISAPI/ContentMgmt/search')
    
    # Boshqa sozlamalar
    TIMEOUT = int(os.getenv('TIMEOUT', 30))
    RETRY_COUNT = int(os.getenv('RETRY_COUNT', 3))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    @property
    def base_url(self):
        """Asosiy URL ni qaytaradi"""
        return f"{self.PROTOCOL}://{self.HOST}:{self.PORT}"
    
    def get_api_url(self, endpoint):
        """API URL ni qaytaradi"""
        return f"{self.base_url}/{endpoint}"
    
    @property
    def device_type(self):
        """Qurilma turini aniqlaydi"""
        return "access_control"  # DS-K1T341CM access control qurilmasi
