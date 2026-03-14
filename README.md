# TecnoChat - Aqlli Yordamchi Robot

TecnoChat - bu o'zbek tilida gapiradigan aqlli yordamchi robot interfeysi. U foydalanuvchi bilan suhbat quradi, ovozli buyruqlarni tushunadi va javob beradi.

## Xususiyatlari

- 🎤 Ovozli tanish (Speech Recognition)
- 🤖 AI bilan suhbat (Groq API orqali)
- 🔊 Ovozli sintez (Silero TTS)
- 👁️ Animatsion robot yuzi
- 📱 Zamonaviy PyQt5 interfeysi
- 🇺🇿 To'liq o'zbek tili qo'llab-quvvatlashi

## Texnologiyalar va Kutubxonalar

### Asosiy Kutubxonalar:
- **PyQt5** - Grafik interfeys uchun
- **torch** - Silero TTS modeli uchun
- **sounddevice** - Audio ijro etish uchun
- **SpeechRecognition** - Ovozni matnga aylantirish uchun
- **groq** - Groq API bilan integratsiya uchun
- **numpy** - Raqamli hisoblashlar uchun

### Tashqi Xizmatlar:
- **Groq API** - AI javoblari uchun (llama-3.3-70b-versatile modeli)
- **Google Speech Recognition** - Ovozni tanish uchun
- **Silero TTS** - O'zbek tilida ovozli sintez uchun

## O'rnatish

1. Repozitoriyani kloning:
```bash
git clone https://github.com/username/techno-chat.git
cd techno-chat
```

2. Python 3.8+ o'rnatilganligini tekshiring

3. Kerakli kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

4. Groq API kalitini oling:
   - [Groq Console](https://console.groq.com/) ga o'ting
   - Hisob yarating va API kalitini oling
   - `GROQ_API_KEY` o'zgaruvchisiga kalitni kiriting

## Ishga Tushirish

```bash
python robot_face.py
```

## Foydalanish

1. Dastur ishga tushgandan so'ng robot tayyor holatiga keladi
2. Mikrofonga gapiring (o'zbek tilida)
3. Robot sizning so'rovingizni tushunadi va AI orqali javob beradi
4. Javob o'zbek tilida ovozli eshitiladi

## Dastur Tuzilishi

```
├── robot_face.py          # Asosiy dastur fayli
├── requirements.txt       # Kerakli kutubxonalar ro'yxati
├── README.md             # Hujjatlar
└── .gitignore           # Git uchun ignore fayli
```

## Asosiy Sinflar

- **RobotFace** - Asosiy interfeys klassi
- **RobotSignals** - Signal klassi (threadlar o'rtasida aloqa uchun)

## Konfiguratsiya

Dasturda quyidagi sozlamalar mavjud:
- Groq API kaliti
- Tili: o'zbek (uz-UZ)
- TTS modeli: Silero v3_uz
- Speaker: dilnavoz

## Talablar

- Python 3.8+
- Windows/Linux/MacOS
- Mikrofon
- Internet ulanishi (Groq API uchun)
- Kamida 4GB RAM

## Xavfsizlik

⚠️ **Muhim**: API kalitlaringizni xavfsiz saqlang! 
- Hech qachon API kalitini koddan tashqari saqlamang
- `.env` faylidan foydalaning
- GitHub'ga API kalitini yuklamang

## Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi.

## Muallif

Maruf - 2026-yilda yaratilgan

## Bog'liq Manbalar

- [Silero TTS](https://github.com/snakers4/silero-models)
- [Groq API](https://groq.com/)
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
