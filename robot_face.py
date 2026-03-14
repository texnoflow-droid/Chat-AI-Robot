import sys
import threading
import torch
import sounddevice as sd
import speech_recognition as sr
from groq import Groq
import time
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QSplitter
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject
import os

# --- GROQ SOZLAMALARI ---
# Xavfsizlik uchun API kalitini environment variable'dan olish
GROQ_API_KEY = os.getenv("GROQ_API_KEY", )

if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_API_KEY_HERE":
    print("⚠️ XAVFSIZLIK OGOGHI: Groq API kalit sozlanmagan!")
    print("Iltimos, GROQ_API_KEY environment variable'ini o'rnating:")
    print("export GROQ_API_KEY='sizning_api_kalitingiz'")
    print("Yoki .env fayl yarating va quyidagini yozing:")
    print("GROQ_API_KEY=sizning_api_kalitingiz")

client = Groq(api_key=GROQ_API_KEY)

class RobotSignals(QObject):
    voice_detected = pyqtSignal(bool)
    status_update = pyqtSignal(str)
    text_received = pyqtSignal(str)
    audio_amplitude = pyqtSignal(float)

class RobotFace(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = RobotSignals()
        self.signals.voice_detected.connect(self.toggle_layout)
        self.signals.status_update.connect(self.update_status)
        self.signals.text_received.connect(self.display_text)
        self.signals.audio_amplitude.connect(self.update_mouth_viz)
        
        self.recognizer = sr.Recognizer()
        self.is_speaking = False
        
        # Silero TTS yuklash
        self.device = torch.device('cpu')
        try:
            self.model_tts, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                             model='silero_tts', language='uz', speaker='v3_uz')
            self.model_tts.to(self.device)
            print("✅ Silero TTS modeli muvaffaqiyatli yuklandi")
        except Exception as e:
            print(f"❌ TTS modelini yuklashda xatolik: {e}")
            print("Internet ulanishini tekshiring")
            sys.exit(1)
        
        self.initUI()
        
        self.listen_thread = threading.Thread(target=self.start_conversation, daemon=True)
        self.listen_thread.start()

    def initUI(self):
        self.setStyleSheet("background-color: #000000;")
        self.showFullScreen()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        # --- TEPADAGI STATUS BAR ---
        self.top_status = QLabel("ROBOT TAYYOR")
        self.top_status.setFixedHeight(60)
        self.top_status.setAlignment(Qt.AlignCenter)
        self.top_status.setStyleSheet("color: #00FFFF; font-size: 24px; font-weight: bold; background-color: #111111; border-bottom: 2px solid #00FFFF;")
        self.layout.addWidget(self.top_status)
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(0)
        
        # --- CHAP PANEL (YUZ) ---
        self.face_widget = QWidget()
        self.face_layout = QVBoxLayout(self.face_widget)
        self.face_layout.addStretch(1)
        
        eyes_layout = QHBoxLayout()
        self.l_eye = QFrame(); self.l_eye.setFixedSize(150, 150)
        self.l_eye.setStyleSheet("background-color: #00FFFF; border-radius: 25px; border: 4px solid #008B8B;")
        self.r_eye = QFrame(); self.r_eye.setFixedSize(150, 150)
        self.r_eye.setStyleSheet("background-color: #00FFFF; border-radius: 25px; border: 4px solid #008B8B;")
        eyes_layout.addStretch(1); eyes_layout.addWidget(self.l_eye); eyes_layout.addSpacing(120); eyes_layout.addWidget(self.r_eye); eyes_layout.addStretch(1)
        self.face_layout.addLayout(eyes_layout)
        self.face_layout.addSpacing(80)
        
        self.mouth = QFrame(); self.mouth.setFixedSize(400, 20)
        self.mouth.setStyleSheet("background-color: #00FFFF; border-radius: 10px;")
        m_lay = QHBoxLayout(); m_lay.addStretch(1); m_lay.addWidget(self.mouth); m_lay.addStretch(1)
        self.face_layout.addLayout(m_lay)
        self.face_layout.addStretch(1)
        
        # --- O'NG PANEL (MATN) ---
        self.text_widget = QWidget()
        self.text_widget.setStyleSheet("background-color: #050505; border-left: 2px solid #00FFFF;")
        self.text_lay = QVBoxLayout(self.text_widget)
        self.text_display = QLabel("")
        self.text_display.setStyleSheet("color: white; font-size: 26px; font-weight: bold; padding: 20px;")
        self.text_display.setWordWrap(True)
        self.text_lay.addWidget(self.text_display)
        self.text_lay.addStretch(1)
        
        self.splitter.addWidget(self.face_widget)
        self.splitter.addWidget(self.text_widget)
        self.layout.addWidget(self.splitter)
        
        self.text_widget.setVisible(False)
        self.splitter.setSizes([self.width(), 0])
        self.blink_timer = QTimer(); self.blink_timer.timeout.connect(self.blink); self.blink_timer.start(3000)

    def toggle_layout(self, is_speaking):
        self.is_speaking = is_speaking
        if is_speaking:
            self.text_widget.setVisible(True)
            self.splitter.setSizes([self.width()//2, self.width()//2])
            self.mouth.setStyleSheet("background-color: #FF00FF; border-radius: 20px; border: 3px solid white;")
        else:
            # Robot gapirib bo'lgach 2 soniyadan keyin ekran joyiga qaytadi
            QTimer.singleShot(2000, self.reset_ui)

    def reset_ui(self):
        if not self.is_speaking:
            self.text_widget.setVisible(False)
            self.splitter.setSizes([self.width(), 0])
            self.mouth.setFixedSize(400, 20)
            self.mouth.setStyleSheet("background-color: #00FFFF; border-radius: 10px;")
            self.signals.status_update.emit("ROBOT TAYYOR")

    def update_mouth_viz(self, amp):
        if self.is_speaking:
            h = int(20 + (amp * 160))
            w = int(400 - (amp * 50))
            self.mouth.setFixedSize(w, h)

    def update_status(self, t): self.top_status.setText(t.upper())
    def display_text(self, t): self.text_display.setText(t)
    
    def blink(self):
        if not self.is_speaking:
            self.l_eye.setFixedHeight(10); self.r_eye.setFixedHeight(10)
            QTimer.singleShot(150, lambda: (self.l_eye.setFixedHeight(150), self.r_eye.setFixedHeight(150)))

    def get_ai_reply(self, text):
        try:
            # Shaxsiyat ko'rsatmalari
            prompt = (
                "Sening isming - TecnoChat. Sen Maruf tomonidan 2026-yilda yaratilgan aqlli yordamchisan. "
                "Agar kimsan yoki seni kim yaratgan deb so'rashsa, albatta 'Meni 2026-yilda Maruf yaratgan' deb javob ber. "
                "Boshqa savollarga (tarix, fan, Amir Temur va h.k.) juda aniq va aqlli javob ber. "
                "Javoblar o'zbek tilida qisqa va tushunarli bo'lsin."
            )
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": prompt},
                          {"role": "user", "content": text}]
            )
            return res.choices[0].message.content
        except Exception as e:
            print(f"AI javobida xatolik: {e}")
            return "Kechirasiz, ma'lumot olishda xatolik yuz berdi."

    def speak_dynamic(self, text):
        try:
            audio = self.model_tts.apply_tts(text=text, speaker='dilnavoz', sample_rate=24000)
            self.signals.voice_detected.emit(True)
            self.signals.status_update.emit("ROBOT GAPIRMOQDA...")
            
            def cb(indata, f, t, s):
                a = np.linalg.norm(indata) / np.sqrt(len(indata))
                self.signals.audio_amplitude.emit(min(1.0, a * 12))
            
            with sd.OutputStream(samplerate=24000, callback=cb):
                sd.play(audio, 24000)
                sd.wait()
            self.signals.voice_detected.emit(False)
        except Exception as e:
            print(f"TTS xatolik: {e}")
            self.signals.voice_detected.emit(False)

    def start_conversation(self):
        while True:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                try:
                    self.signals.status_update.emit("TINGLAYAPMAN...")
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=8)
                    
                    self.signals.status_update.emit("O'YLAYAPMAN...")
                    u_input = self.recognizer.google_recognize(audio, language="uz-UZ")
                    
                    print(f"Foydalanuvchi: {u_input}")
                    reply = self.get_ai_reply(u_input)
                    print(f"Robot: {reply}")
                    
                    self.signals.text_received.emit(reply)
                    self.speak_dynamic(reply)
                except sr.UnknownValueError:
                    # Agar gapni tushunmasa
                    msg = "Kechirasiz, tushunolmadim. Iltimos, qayta ayting."
                    self.signals.text_received.emit(msg)
                    self.speak_dynamic(msg)
                except Exception as e:
                    print(f"Suqbatda xatolik: {e}")
                    continue

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RobotFace()
    ex.show()
    sys.exit(app.exec_())
