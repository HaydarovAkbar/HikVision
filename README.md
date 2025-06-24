# HikVision Ma'lumotlar Parser

## Loyiha haqida
Bu loyiha HikVision kamera tizimlaridan ma'lumotlarni olish va parsing qilish uchun mo'ljallangan. Python dasturlash tilida yozilgan va RESTful API orqali HikVision platformasi bilan ishlaydi.

## Xususiyatlar
- ✅ HikVision ISAPI bilan ishlash
- ✅ Qurilma ma'lumotlarini olish
- ✅ Video kanallar ma'lumotlari
- ✅ Streaming sozlamalari
- ✅ PTZ (Pan-Tilt-Zoom) ma'lumotlari
- ✅ JSON va CSV formatlarida eksport
- ✅ Xato boshqaruvi va logging
- ✅ Rangli konsolda chiqarish
- ✅ Progress bar bilan ishlash

## O'rnatish

### 1. Repository ni klonlash
```bash
git clone <repository_url>
cd HikVision
```

### 2. Virtual muhit yaratish (tavsiya etiladi)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate     # Windows
```

### 3. Bog'liqliklarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Konfiguratsiyani sozlash
`config/settings.env` faylida quyidagi parametrlarni sozlang:
```env
HIKVISION_HOST=172.18.18.60
HIKVISION_USERNAME=admin
HIKVISION_PASSWORD=qwerty@321
HIKVISION_PORT=80
HIKVISION_PROTOCOL=http
```

## Foydalanish

### Asosiy skriptni ishga tushirish
```bash
python main.py
```

Bu skript quyidagi amallarni bajaradi:
1. HikVision serveriga ulanadi
2. Qurilma ma'lumotlarini oladi
3. Video kanallar ma'lumotlarini yig'adi
4. Streaming sozlamalarini oladi
5. PTZ ma'lumotlarini tekshiradi
6. Barcha ma'lumotlarni JSON va CSV formatlarida saqlaydi

### Programmatik foydalanish
```python
from src.config import HikVisionConfig
from src.hikvision_api import HikVisionAPI
from src.parser import HikVisionParser

# Konfiguratsiya yaratish
config = HikVisionConfig()

# API obyektini yaratish
api = HikVisionAPI(config)

# Ulanishni tekshirish
if api.test_connection():
    print("Ulanish muvaffaqiyatli!")
    
    # Parser yaratish
    parser = HikVisionParser(api)
    
    # To'liq ma'lumotlarni olish
    system_info = parser.get_full_system_info()
    
    # JSON ga saqlash
    parser.export_to_json(system_info, "system_info.json")
```

## Loyiha strukturasi
```
HikVision/
├── src/
│   ├── __init__.py
│   ├── config.py          # Konfiguratsiya boshqaruvi
│   ├── hikvision_api.py   # HikVision API bilan ishlash
│   └── parser.py          # Ma'lumotlarni parsing qilish
├── tests/
│   └── test_api.py        # Unit testlar
├── config/
│   └── settings.env       # Konfiguratsiya fayli
├── docs/                  # Hujjatlar
├── output/                # Natija fayllari (avtomatik yaratiladi)
├── main.py               # Asosiy skript
├── requirements.txt      # Python bog'liqliklar
└── README.md            # Bu fayl
```

## API Endpoints
Loyiha quyidagi HikVision ISAPI endpoints bilan ishlaydi:

- `ISAPI/System/deviceInfo` - Qurilma ma'lumotlari
- `ISAPI/System/Video/inputs` - Video kirish kanallari
- `ISAPI/Streaming/channels` - Streaming kanallar
- `ISAPI/PTZCtrl/channels/{id}/capabilities` - PTZ imkoniyatlari
- `ISAPI/Event/notification` - Hodisalar
- `ISAPI/ContentMgmt/search` - Yozuvlarni qidirish

## Chiqish formatlari

### JSON Format
Barcha tizim ma'lumotlari to'liq JSON formatida saqlanadi:
```json
{
  "timestamp": "2024-12-24T10:30:00",
  "device_info": {
    "device_name": "Camera-01",
    "model": "DS-2CD2086G2-I",
    "serial_number": "ABC123456",
    "firmware_version": "V5.7.0"
  },
  "channels": [...],
  "streaming_channels": [...],
  "ptz_info": {...}
}
```

### CSV Format
Har bir ma'lumot turi alohida CSV faylida saqlanadi:
- `hikvision_channels_YYYYMMDD_HHMMSS.csv` - Video kanallar
- `hikvision_streaming_YYYYMMDD_HHMMSS.csv` - Streaming kanallar

## Testlar
```bash
# Barcha testlarni ishga tushirish
python -m pytest tests/

# Yoki unittest bilan
python tests/test_api.py
```

## Xato tuzatish

### Umumiy xatolar

1. **Ulanish xatosi**
   - Server IP manzilini tekshiring
   - Username va parolni tasdiqlang
   - Network ulanishini tekshiring

2. **Autentifikatsiya xatosi**
   - HikVision foydalanuvchi hisobi faol ekanligini tekshiring
   - Parol to'g'riligini tasdiqlang
   - Foydalanuvchi huquqlarini tekshiring

3. **API xatosi**
   - HikVision versiyasi ISAPI ni qo'llab-quvvatlashini tekshiring
   - Firewall sozlamalarini tekshiring

### Debug rejimi
Qo'shimcha ma'lumotlar uchun `config/settings.env` da:
```env
DEBUG=True
```

## Xavfsizlik
- Parollarni kodda qoldirmang
- `.env` fayllarini git ga qo'shmang
- HTTPS ni iloji bo'lsa ishlatinga
- Foydalanuvchi huquqlarini cheklang

## Hissa qo'shish
1. Repository ni fork qiling
2. Feature branch yarating
3. O'zgarishlaringizni commit qiling
4. Pull request yuboring

## Litsenziya
MIT License

## Qo'llab-quvvatlash
Savollar yoki muammolar uchun issue yarating yoki developer bilan bog'laning.

## O'zgarishlar tarixi
- v1.0.0 - Dastlabki versiya
  - Asosiy API funksionallik
  - JSON/CSV eksport
  - Unit testlar
  - Ranglikonsolda chiqarish

## Istiqboldagi rejalar
- [ ] Real-time hodisalarni kuzatish
- [ ] Video oqimlarini saqlash
- [ ] Web dashboard yaratish
- [ ] Docker qo'llab-quvvatlash
- [ ] Bulk kamera boshqaruvi
- [ ] Alert tizimi
