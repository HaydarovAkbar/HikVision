import requests
import xml.etree.ElementTree as ET
import json
import logging
from datetime import datetime
from requests.auth import HTTPDigestAuth
from typing import Dict, List, Optional, Any
from .config import HikVisionConfig

class HikVisionAPI:
    """HikVision API bilan ishlash uchun asosiy sinf - Access Control uchun moslashtirilgan"""
    
    def __init__(self, config: HikVisionConfig = None):
        """
        HikVision API ni ishga tushirish
        
        Args:
            config: HikVisionConfig obyekti
        """
        self.config = config or HikVisionConfig()
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(self.config.USERNAME, self.config.PASSWORD)
        self.session.timeout = self.config.TIMEOUT
        
        # Logging sozlash
        logging.basicConfig(
            level=logging.DEBUG if self.config.DEBUG else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        API ga so'rov yuborish
        
        Args:
            method: HTTP metodi (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            **kwargs: Qo'shimcha parametrlar
            
        Returns:
            requests.Response obyekti
        """
        url = self.config.get_api_url(endpoint)
        
        try:
            self.logger.debug(f"So'rov yuborilmoqda: {method} {url}")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            self.logger.debug(f"Javob olindi: {response.status_code}")
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"So'rov yuborishda xatolik: {e}")
            raise
    
    def _parse_xml_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        XML javobni dictionary ga aylantirish
        
        Args:
            response: requests.Response obyekti
            
        Returns:
            Dictionary
        """
        try:
            root = ET.fromstring(response.content)
            return self._xml_to_dict(root)
        except ET.ParseError as e:
            self.logger.error(f"XML parsing xatolik: {e}")
            return {}
    
    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """
        XML elementni dictionary ga aylantirish
        
        Args:
            element: XML elementi
            
        Returns:
            Dictionary
        """
        result = {}
        
        # Atributlarni qo'shish
        if element.attrib:
            result.update(element.attrib)
        
        # Matnni qo'shish
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text.strip()
            result['text'] = element.text.strip()
        
        # Bolalarni qo'shish
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Qurilma ma'lumotlarini olish
        
        Returns:
            Qurilma ma'lumotlari
        """
        try:
            response = self._make_request('GET', self.config.API_DEVICE_INFO)
            return self._parse_xml_response(response)
        except Exception as e:
            self.logger.error(f"Qurilma ma'lumotlarini olishda xatolik: {e}")
            return {}
    
    def get_access_control_events(self, start_time: str = None, end_time: str = None) -> List[Dict[str, Any]]:
        """
        Access Control hodisalarini olish
        
        Args:
            start_time: Boshlanish vaqti (ISO format)
            end_time: Tugash vaqti (ISO format)
            
        Returns:
            Hodisalar ro'yxati
        """
        try:
            params = {}
            if start_time:
                params['startTime'] = start_time
            if end_time:
                params['endTime'] = end_time
            
            response = self._make_request('GET', self.config.API_ACCESS_CONTROL, params=params)
            data = self._parse_xml_response(response)
            
            events = []
            if 'AcsEventList' in data and 'AcsEvent' in data['AcsEventList']:
                event_data = data['AcsEventList']['AcsEvent']
                if isinstance(event_data, list):
                    events = event_data
                else:
                    events = [event_data]
            
            return events
        except Exception as e:
            self.logger.error(f"Access Control hodisalarini olishda xatolik: {e}")
            return []
    
    def get_card_info(self, card_no: str = None) -> List[Dict[str, Any]]:
        """
        Karta ma'lumotlarini olish
        
        Args:
            card_no: Karta raqami (agar berilmasa, barcha kartalar)
            
        Returns:
            Karta ma'lumotlari ro'yxati
        """
        try:
            endpoint = self.config.API_CARD_INFO
            if card_no:
                endpoint = f"{endpoint}/{card_no}"
            
            response = self._make_request('GET', endpoint)
            data = self._parse_xml_response(response)
            
            cards = []
            if 'CardInfoList' in data and 'CardInfo' in data['CardInfoList']:
                card_data = data['CardInfoList']['CardInfo']
                if isinstance(card_data, list):
                    cards = card_data
                else:
                    cards = [card_data]
            
            return cards
        except Exception as e:
            self.logger.error(f"Karta ma'lumotlarini olishda xatolik: {e}")
            return []
    
    def get_user_info(self, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Foydalanuvchi ma'lumotlarini olish
        
        Args:
            user_id: Foydalanuvchi ID si (agar berilmasa, barcha foydalanuvchilar)
            
        Returns:
            Foydalanuvchi ma'lumotlari ro'yxati
        """
        try:
            endpoint = self.config.API_USER_INFO
            if user_id:
                endpoint = f"{endpoint}/{user_id}"
            
            response = self._make_request('GET', endpoint)
            data = self._parse_xml_response(response)
            
            users = []
            if 'UserInfoList' in data and 'UserInfo' in data['UserInfoList']:
                user_data = data['UserInfoList']['UserInfo']
                if isinstance(user_data, list):
                    users = user_data
                else:
                    users = [user_data]
            
            return users
        except Exception as e:
            self.logger.error(f"Foydalanuvchi ma'lumotlarini olishda xatolik: {e}")
            return []
    
    def get_door_status(self, door_id: int = 1) -> Dict[str, Any]:
        """
        Eshik holatini olish
        
        Args:
            door_id: Eshik ID si
            
        Returns:
            Eshik holati ma'lumotlari
        """
        try:
            endpoint = f"{self.config.API_DOOR_STATUS}/{door_id}/status"
            response = self._make_request('GET', endpoint)
            return self._parse_xml_response(response)
        except Exception as e:
            self.logger.error(f"Eshik holatini olishda xatolik: {e}")
            return {}
    
    def control_door(self, door_id: int = 1, command: str = "open") -> bool:
        """
        Eshikni boshqarish
        
        Args:
            door_id: Eshik ID si
            command: Buyruq ("open", "close", "always_open", "always_close")
            
        Returns:
            True agar muvaffaqiyatli bo'lsa
        """
        try:
            control_data = f"""<?xml version="1.0" encoding="UTF-8"?>
            <RemoteControlDoor>
                <cmd>{command}</cmd>
            </RemoteControlDoor>"""
            
            endpoint = f"{self.config.API_DOOR_CONTROL}/{door_id}"
            headers = {'Content-Type': 'application/xml'}
            response = self._make_request('PUT', endpoint, data=control_data, headers=headers)
            
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Eshikni boshqarishda xatolik: {e}")
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Qurilma imkoniyatlarini olish
        
        Returns:
            Imkoniyatlar ma'lumotlari
        """
        try:
            response = self._make_request('GET', self.config.API_CAPABILITIES)
            return self._parse_xml_response(response)
        except Exception as e:
            self.logger.error(f"Imkoniyatlarni olishda xatolik: {e}")
            return {}
    
    def get_time_config(self) -> Dict[str, Any]:
        """
        Vaqt sozlamalarini olish
        
        Returns:
            Vaqt sozlamalari
        """
        try:
            response = self._make_request('GET', self.config.API_TIME_CONFIG)
            return self._parse_xml_response(response)
        except Exception as e:
            self.logger.error(f"Vaqt sozlamalarini olishda xatolik: {e}")
            return {}
    
    def get_network_config(self) -> Dict[str, Any]:
        """
        Tarmoq sozlamalarini olish
        
        Returns:
            Tarmoq sozlamalari
        """
        try:
            response = self._make_request('GET', self.config.API_NETWORK_CONFIG)
            return self._parse_xml_response(response)
        except Exception as e:
            self.logger.error(f"Tarmoq sozlamalarini olishda xatolik: {e}")
            return {}
    
    # Kameralar uchun eski metodlar (agar access control qurilmasida kamera bo'lsa)
    def get_channels(self) -> List[Dict[str, Any]]:
        """
        Video kanallarini olish (agar mavjud bo'lsa)
        
        Returns:
            Kanallar ro'yxati
        """
        try:
            response = self._make_request('GET', self.config.API_CHANNELS)
            data = self._parse_xml_response(response)
            
            channels = []
            if 'VideoInputChannelList' in data:
                channel_list = data['VideoInputChannelList']
                if 'VideoInputChannel' in channel_list:
                    channel_data = channel_list['VideoInputChannel']
                    if isinstance(channel_data, list):
                        channels = channel_data
                    else:
                        channels = [channel_data]
            
            return channels
        except Exception as e:
            self.logger.error(f"Kanallarni olishda xatolik: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Ulanishni tekshirish
        
        Returns:
            True agar ulanish muvaffaqiyatli bo'lsa
        """
        try:
            device_info = self.get_device_info()
            if device_info:
                self.logger.info("HikVision access control qurilmasiga muvaffaqiyatli ulanildi")
                return True
            else:
                self.logger.error("HikVision access control qurilmasiga ulanish muvaffaqiyatsiz")
                return False
        except Exception as e:
            self.logger.error(f"Ulanishni tekshirishda xatolik: {e}")
            return False
