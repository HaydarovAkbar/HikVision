#!/usr/bin/env python3
"""
HikVision Ma'lumotlar Parser - Interaktiv versiya
Bu skript sizdan kamera ma'lumotlarini so'raydi va keyin parsing qiladi
"""

import sys
import os
import json
import getpass
from datetime import datetime
from colorama import init, Fore, Style
from tqdm import tqdm

# Loyiha yo'lini qo'shish
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import HikVisionConfig
from src.hikvision_api import HikVisionAPI
from src.parser import HikVisionParser

# Ranglarni ishga tushirish
init()

def print_banner():
    """Banner chiqarish"""
    print(Fore.CYAN + """
    ╔═══════════════════════════════════════════════════════════╗
    ║              HikVision Data Parser (Interactive)          ║
    ║                      v1.0.0                               ║
    ╚═══════════════════════════════════════════════════════════╝
    """ + Style.RESET_ALL)

def print_success(message):
    """Muvaffaqiyat xabarini chiqarish"""
    print(Fore.GREEN + "✓ " + message + Style.RESET_ALL)

def print_error(message):
    """Xato xabarini chiqarish"""
    print(Fore.RED + "✗ " + message + Style.RESET_ALL)

def print_info(message):
    """Ma'lumot xabarini chiqarish"""
    print(Fore.YELLOW + "ℹ " + message + Style.RESET_ALL)

def print_warning(message):
    """Ogohlantirish xabarini chiqarish"""
    print(Fore.MAGENTA + "⚠ " + message + Style.RESET_ALL)

def get_camera_credentials():
    """Foydalanuvchidan kamera ma'lumotlarini olish"""
    print(Fore.CYAN + "\n" + "="*60)
    print("           HIKVISION KAMERA MA'LUMOTLARI")
    print("="*60 + Style.RESET_ALL)
    
    # IP manzil
    while True:
        host = input(f"\n{Fore.WHITE}Kamera IP manzili{Style.RESET_ALL} (masalan: 192.168.1.100): ").strip()
        if host:
            break
        print_error("IP manzil kiritish majburiy!")
    
    # Username
    username = input(f"{Fore.WHITE}Username{Style.RESET_ALL} [admin]: ").strip()
    if not username:
        username = "admin"
    
    # Password
    while True:
        password = getpass.getpass(f"{Fore.WHITE}Password{Style.RESET_ALL}: ")
        if password:
            break
        print_error("Parol kiritish majburiy!")
    
    # Port
    port_input = input(f"{Fore.WHITE}Port{Style.RESET_ALL} [80]: ").strip()
    try:
        port = int(port_input) if port_input else 80
    except ValueError:
        port = 80
        print_warning("Noto'g'ri port, standart 80 ishlatiladi")
    
    # Protocol
    protocol_input = input(f"{Fore.WHITE}Protocol{Style.RESET_ALL} [http]: ").strip().lower()
    protocol = protocol_input if protocol_input in ['http', 'https'] else 'http'
    
    return {
        'host': host,
        'username': username,
        'password': password,
        'port': port,
        'protocol': protocol
    }

def create_custom_config(credentials):
    """Foydalanuvchi ma'lumotlari asosida konfiguratsiya yaratish"""
    
    class CustomConfig:
        def __init__(self, creds):
            self.HOST = creds['host']
            self.USERNAME = creds['username']
            self.PASSWORD = creds['password']
            self.PORT = creds['port']
            self.PROTOCOL = creds['protocol']
            
            # API yo'llari
            self.API_VERSION = 'ISAPI/System/deviceInfo'
            self.API_CHANNELS = 'ISAPI/System/Video/inputs'
            self.API_STREAMING = 'ISAPI/Streaming/channels'
            self.API_PTZ = 'ISAPI/PTZCtrl/channels'
            self.API_EVENTS = 'ISAPI/Event/notification'
            self.API_PLAYBACK = 'ISAPI/ContentMgmt/search'
            
            # Boshqa sozlamalar
            self.TIMEOUT = 30
            self.RETRY_COUNT = 3
            self.DEBUG = True
        
        @property
        def base_url(self):
            return f"{self.PROTOCOL}://{self.HOST}:{self.PORT}"
        
        def get_api_url(self, endpoint):
            return f"{self.base_url}/{endpoint}"
    
    return CustomConfig(credentials)

def create_output_directory():
    """Natija papkasini yaratish"""
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print_success(f"'{output_dir}' papkasi yaratildi")
    return output_dir

def display_summary(system_info):
    """Ma'lumotlar xulasasini ko'rsatish"""
    print(Fore.CYAN + "\n" + "="*60)
    print("                    MA'LUMOTLAR XULOSASI")
    print("="*60 + Style.RESET_ALL)
    
    # Qurilma ma'lumotlari
    device_info = system_info.get('device_info', {})
    if device_info:
        print(f"{Fore.WHITE}Qurilma nomi:{Style.RESET_ALL} {device_info.get('device_name', 'N/A')}")
        print(f"{Fore.WHITE}Model:{Style.RESET_ALL} {device_info.get('model', 'N/A')}")
        print(f"{Fore.WHITE}Serial raqam:{Style.RESET_ALL} {device_info.get('serial_number', 'N/A')}")
        print(f"{Fore.WHITE}Firmware:{Style.RESET_ALL} {device_info.get('firmware_version', 'N/A')}")
        print(f"{Fore.WHITE}IP manzil:{Style.RESET_ALL} {device_info.get('ip_address', 'N/A')}")
    
    # Kanallar
    channels = system_info.get('channels', [])
    streaming_channels = system_info.get('streaming_channels', [])
    
    print(f"\n{Fore.WHITE}Video kanallar soni:{Style.RESET_ALL} {len(channels)}")
    print(f"{Fore.WHITE}Streaming kanallar soni:{Style.RESET_ALL} {len(streaming_channels)}")
    
    # Faol kanallar
    active_channels = [ch for ch in channels if ch.get('enabled', False)]
    active_streaming = [ch for ch in streaming_channels if ch.get('enabled', False)]
    
    print(f"{Fore.WHITE}Faol video kanallar:{Style.RESET_ALL} {len(active_channels)}")
    print(f"{Fore.WHITE}Faol streaming kanallar:{Style.RESET_ALL} {len(active_streaming)}")
    
    # PTZ ma'lumotlari
    ptz_info = system_info.get('ptz_info', {})
    if ptz_info.get('ptz_supported', False):
        print(f"{Fore.WHITE}PTZ qo'llab-quvvatlash:{Style.RESET_ALL} Ha")
    else:
        print(f"{Fore.WHITE}PTZ qo'llab-quvvatlash:{Style.RESET_ALL} Yo'q")
    
    print(Fore.CYAN + "="*60 + Style.RESET_ALL + "\n")

def main():
    """Asosiy funksiya"""
    print_banner()
    
    try:
        # Foydalanuvchidan ma'lumotlarni olish
        credentials = get_camera_credentials()
        
        # Konfiguratsiya yaratish
        print_info("Konfiguratsiya yaratilmoqda...")
        config = create_custom_config(credentials)
        
        # Ulanish ma'lumotlarini ko'rsatish
        print(f"\n{Fore.CYAN}Ulanish ma'lumotlari:{Style.RESET_ALL}")
        print(f"Server: {config.base_url}")
        print(f"Username: {config.USERNAME}")
        print(f"Password: {'*' * len(config.PASSWORD)}")
        
        # API obyektini yaratish
        print_info("\nHikVision API ga ulanmoqda...")
        api = HikVisionAPI(config)
        
        # Ulanishni tekshirish
        print_info("Ulanish tekshirilmoqda...")
        if not api.test_connection():
            print_error("HikVision serveriga ulanib bo'lmadi!")
            print_error("Quyidagilarni tekshiring:")
            print_error("• IP manzil to'g'ri kiritilganmi?")
            print_error("• Username va parol to'g'rimi?")
            print_error("• Kamera tarmoqda faolmi?")
            print_error("• Port to'g'ri sozlanganmi?")
            return False
        
        print_success("HikVision serveriga muvaffaqiyatli ulanildi!")
        
        # Parser yaratish
        parser = HikVisionParser(api)
        
        # Natija papkasini yaratish
        output_dir = create_output_directory()
        
        # Ma'lumotlarni olish
        print_info("Tizim ma'lumotlari olinmoqda...")
        
        with tqdm(total=5, desc="Ma'lumotlar olinmoqda") as pbar:
            # To'liq tizim ma'lumotlari
            pbar.set_description("Qurilma ma'lumotlari...")
            system_info = parser.get_full_system_info()
            pbar.update(1)
            
            # Natijalarni chiqarish
            pbar.set_description("Natijalar tayyorlanmoqda...")
            
            # JSON formatda saqlash
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_file = os.path.join(output_dir, f"hikvision_data_{timestamp}.json")
            
            if parser.export_to_json(system_info, json_file):
                print_success(f"Ma'lumotlar JSON formatda saqlandi: {json_file}")
            else:
                print_error("JSON formatda saqlashda xatolik!")
            pbar.update(1)
            
            # CSV formatda saqlash (kanallar uchun)
            if system_info.get('channels'):
                csv_file = os.path.join(output_dir, f"hikvision_channels_{timestamp}.csv")
                if parser.export_to_csv(system_info['channels'], csv_file):
                    print_success(f"Kanallar CSV formatda saqlandi: {csv_file}")
                else:
                    print_error("CSV formatda saqlashda xatolik!")
            pbar.update(1)
            
            # Streaming kanallar CSV
            if system_info.get('streaming_channels'):
                csv_file = os.path.join(output_dir, f"hikvision_streaming_{timestamp}.csv")
                if parser.export_to_csv(system_info['streaming_channels'], csv_file):
                    print_success(f"Streaming kanallar CSV formatda saqlandi: {csv_file}")
                else:
                    print_error("Streaming CSV saqlashda xatolik!")
            pbar.update(1)
            
            pbar.set_description("Yakunlanmoqda...")
            pbar.update(1)
        
        # Ma'lumotlar xulosasini ko'rsatish
        display_summary(system_info)
        
        print_success("Barcha ma'lumotlar muvaffaqiyatli olindi va saqlandi!")
        
        # Konfiguratsiyani saqlaymi?
        save_config = input(f"\n{Fore.WHITE}Ushbu konfiguratsiyani keyingi foydalanish uchun saqlaysizmi? (y/N):{Style.RESET_ALL} ").strip().lower()
        if save_config in ['y', 'yes', 'ha']:
            config_content = f"""# HikVision konfiguratsiyasi
HIKVISION_HOST={config.HOST}
HIKVISION_USERNAME={config.USERNAME}
HIKVISION_PASSWORD={config.PASSWORD}
HIKVISION_PORT={config.PORT}
HIKVISION_PROTOCOL={config.PROTOCOL}

# API yo'llari
API_VERSION=ISAPI/System/deviceInfo
API_CHANNELS=ISAPI/System/Video/inputs
API_STREAMING=ISAPI/Streaming/channels
API_PTZ=ISAPI/PTZCtrl/channels
API_EVENTS=ISAPI/Event/notification
API_PLAYBACK=ISAPI/ContentMgmt/search

# Boshqa sozlamalar
TIMEOUT=30
RETRY_COUNT=3
DEBUG=True
"""
            with open('config/settings.env', 'w') as f:
                f.write(config_content)
            print_success("Konfiguratsiya saqlandi! Keyingi safar main.py ishlatishingiz mumkin.")
        
        return True
        
    except KeyboardInterrupt:
        print_warning("\nFoydalanuvchi tomonidan to'xtatildi!")
        return False
    except Exception as e:
        print_error(f"Xatolik yuz berdi: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
