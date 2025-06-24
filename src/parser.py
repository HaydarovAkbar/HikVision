import json
import csv
from datetime import datetime
from typing import Dict, List, Any, Optional
from .hikvision_api import HikVisionAPI
from .config import HikVisionConfig

class HikVisionParser:
    """HikVision ma'lumotlarini parsing qilish uchun sinf"""
    
    def __init__(self, api: HikVisionAPI = None):
        """
        Parser ni ishga tushirish
        
        Args:
            api: HikVisionAPI obyekti
        """
        self.api = api or HikVisionAPI()
    
    def parse_device_info(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Qurilma ma'lumotlarini parsing qilish
        
        Args:
            device_info: Qurilma ma'lumotlari
            
        Returns:
            Parsing qilingan ma'lumotlar
        """
        parsed = {
            'timestamp': datetime.now().isoformat(),
            'device_name': '',
            'device_id': '',
            'model': '',
            'serial_number': '',
            'firmware_version': '',
            'mac_address': '',
            'ip_address': '',
            'manufacturer': '',
            'device_type': ''
        }
        
        if 'DeviceInfo' in device_info:
            info = device_info['DeviceInfo']
            parsed.update({
                'device_name': info.get('deviceName', ''),
                'device_id': info.get('deviceID', ''),
                'model': info.get('model', ''),
                'serial_number': info.get('serialNumber', ''),
                'firmware_version': info.get('firmwareVersion', ''),
                'mac_address': info.get('macAddress', ''),
                'ip_address': info.get('ipAddress', ''),
                'manufacturer': info.get('manufacturer', 'HikVision'),
                'device_type': info.get('deviceType', '')
            })
        
        return parsed
    
    def parse_channels(self, channels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Kanallarni parsing qilish
        
        Args:
            channels: Kanallar ro'yxati
            
        Returns:
            Parsing qilingan kanallar
        """
        parsed_channels = []
        
        for channel in channels:
            parsed_channel = {
                'timestamp': datetime.now().isoformat(),
                'channel_id': '',
                'channel_name': '',
                'enabled': False,
                'resolution_height': 0,
                'resolution_width': 0,
                'video_format': '',
                'input_port': '',
                'video_quality': ''
            }
            
            if isinstance(channel, dict):
                parsed_channel.update({
                    'channel_id': channel.get('id', ''),
                    'channel_name': channel.get('channelName', ''),
                    'enabled': channel.get('enabled', 'false').lower() == 'true',
                    'input_port': channel.get('inputPort', ''),
                })
                
                # Video formatini parsing qilish
                if 'videoFormat' in channel:
                    video_format = channel['videoFormat']
                    parsed_channel['video_format'] = video_format
                
                # Rezolyutsiyani parsing qilish
                if 'resolutionHeight' in channel:
                    parsed_channel['resolution_height'] = int(channel.get('resolutionHeight', 0))
                if 'resolutionWidth' in channel:
                    parsed_channel['resolution_width'] = int(channel.get('resolutionWidth', 0))
            
            parsed_channels.append(parsed_channel)
        
        return parsed_channels
    
    def parse_streaming_channels(self, channels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Streaming kanallarni parsing qilish
        
        Args:
            channels: Streaming kanallar ro'yxati
            
        Returns:
            Parsing qilingan streaming kanallar
        """
        parsed_channels = []
        
        for channel in channels:
            parsed_channel = {
                'timestamp': datetime.now().isoformat(),
                'channel_id': '',
                'transport_protocol': '',
                'enabled': False,
                'video_codec_type': '',
                'audio_codec_type': '',
                'video_bitrate': 0,
                'audio_bitrate': 0,
                'video_frame_rate': 0,
                'video_resolution': '',
                'stream_type': ''
            }
            
            if isinstance(channel, dict):
                parsed_channel.update({
                    'channel_id': channel.get('id', ''),
                    'enabled': channel.get('enabled', 'false').lower() == 'true',
                    'transport_protocol': channel.get('Transport', {}).get('Protocol', ''),
                })
                
                # Video ma'lumotlarini parsing qilish
                if 'Video' in channel:
                    video = channel['Video']
                    parsed_channel.update({
                        'video_codec_type': video.get('videoCodecType', ''),
                        'video_bitrate': int(video.get('maxBitrate', 0)),
                        'video_frame_rate': int(video.get('videoFrameRate', 0)),
                        'video_resolution': f"{video.get('videoResolutionWidth', 0)}x{video.get('videoResolutionHeight', 0)}"
                    })
                
                # Audio ma'lumotlarini parsing qilish
                if 'Audio' in channel:
                    audio = channel['Audio']
                    parsed_channel.update({
                        'audio_codec_type': audio.get('audioCompressionType', ''),
                        'audio_bitrate': int(audio.get('audioBitRate', 0))
                    })
            
            parsed_channels.append(parsed_channel)
        
        return parsed_channels
    
    def parse_ptz_info(self, ptz_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        PTZ ma'lumotlarini parsing qilish
        
        Args:
            ptz_info: PTZ ma'lumotlari
            
        Returns:
            Parsing qilingan PTZ ma'lumotlari
        """
        parsed = {
            'timestamp': datetime.now().isoformat(),
            'ptz_supported': False,
            'pan_supported': False,
            'tilt_supported': False,
            'zoom_supported': False,
            'preset_supported': False,
            'patrol_supported': False,
            'max_presets': 0,
            'pan_range': '',
            'tilt_range': '',
            'zoom_range': ''
        }
        
        if 'PTZData' in ptz_info:
            ptz_data = ptz_info['PTZData']
            parsed.update({
                'ptz_supported': True,
                'pan_supported': ptz_data.get('pan', 'false').lower() == 'true',
                'tilt_supported': ptz_data.get('tilt', 'false').lower() == 'true',
                'zoom_supported': ptz_data.get('zoom', 'false').lower() == 'true',
                'preset_supported': ptz_data.get('presetSupport', 'false').lower() == 'true',
                'patrol_supported': ptz_data.get('patrolSupport', 'false').lower() == 'true',
            })
        
        return parsed
    
    def export_to_json(self, data: Any, filename: str) -> bool:
        """
        Ma'lumotlarni JSON faylga eksport qilish
        
        Args:
            data: Eksport qilinadigan ma'lumotlar
            filename: Fayl nomi
            
        Returns:
            True agar muvaffaqiyatli bo'lsa
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"JSON ga eksport qilishda xatolik: {e}")
            return False
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str) -> bool:
        """
        Ma'lumotlarni CSV faylga eksport qilish
        
        Args:
            data: Eksport qilinadigan ma'lumotlar (list of dict)
            filename: Fayl nomi
            
        Returns:
            True agar muvaffaqiyatli bo'lsa
        """
        try:
            if not data:
                return False
            
            fieldnames = data[0].keys()
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            return True
        except Exception as e:
            print(f"CSV ga eksport qilishda xatolik: {e}")
            return False
    
    def get_full_system_info(self) -> Dict[str, Any]:
        """
        To'liq tizim ma'lumotlarini olish va parsing qilish
        
        Returns:
            Barcha ma'lumotlar
        """
        system_info = {
            'timestamp': datetime.now().isoformat(),
            'device_info': {},
            'channels': [],
            'streaming_channels': [],
            'ptz_info': {}
        }
        
        try:
            # Qurilma ma'lumotlari
            device_info = self.api.get_device_info()
            if device_info:
                system_info['device_info'] = self.parse_device_info(device_info)
            
            # Kanallar
            channels = self.api.get_channels()
            if channels:
                system_info['channels'] = self.parse_channels(channels)
            
            # Streaming kanallar
            streaming_channels = self.api.get_streaming_channels()
            if streaming_channels:
                system_info['streaming_channels'] = self.parse_streaming_channels(streaming_channels)
            
            # PTZ ma'lumotlari
            ptz_info = self.api.get_ptz_info()
            if ptz_info:
                system_info['ptz_info'] = self.parse_ptz_info(ptz_info)
        
        except Exception as e:
            print(f"Tizim ma'lumotlarini olishda xatolik: {e}")
        
        return system_info
