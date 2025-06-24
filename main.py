#!/usr/bin/env python3
"""
HikVision Ma'lumotlar Parser
Bu skript HikVision platformasidan ma'lumotlarni olish va parsing qilish uchun
"""

import sys
import os
import json
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
    ║                  HikVision Data Parser                    ║
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
        # Konfiguratsiya yaratish
        print_info("Konfiguratsiya yuklanmoqda...")
        config = HikVisionConfig()
        
        # API obyektini yaratish
        print_info("HikVision API ga ulanmoqda...")
        api = HikVisionAPI(config)
        
        # Ulanishni tekshirish
        print_info("Ulanish tekshirilmoqda...")
        if not api.test_connection():
            print_error("HikVision serveriga ulanib bo'lmadi!")
            print_error(f"Server: {config.base_url}")
            print_error(f"Username: {config.USERNAME}")
            print_error("Konfiguratsiyani tekshiring!")
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
