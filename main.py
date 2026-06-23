import os
import time
import shutil
import itertools
import threading
import pyzipper

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.lang import Builder

# डिफ़ॉल्ट बोरिंग लुक्स को पूरी तरह से हटाकर स्क्रैच से नया मॉडर्न डिज़ाइन
Builder.load_string('''
<ZipCrackerLayout>:
    orientation: 'vertical'
    padding: [25, 40, 25, 25]
    spacing: 20
    canvas.before:
        Color:
            rgba: 0.03, 0.04, 0.06, 1  # अल्ट्रा डार्क बैकग्राउंड (Premium OLED Black)
        Rectangle:
            pos: self.pos
            size: self.size

    # आधुनिक और क्लीन हेडर
    Label:
        text: "[b][color=00FFCC]⚡ ZIP[/color] CRACKER PRO[/b]"
        markup: True
        font_size: '28sp'
        size_hint_y: None
        height: 50
        halign: 'center'

    # इनपुट कार्ड्स का कंटेनर
    BoxLayout:
        orientation: 'vertical'
        spacing: 15
        size_hint_y: None
        height: 280

        # कार्ड 1: फ़ाइल सिलेक्शन
        BoxLayout:
            orientation: 'vertical'
            padding: [15, 10, 15, 10]
            canvas.before:
                Color:
                    rgba: 0.08, 0.1, 0.15, 1  # स्मूथ डार्क ग्रे कार्ड
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [12]
            Label:
                text: "📁 सिलेक्ट ज़िप फ़ाइल"
                font_size: '13sp'
                color: 0.5, 0.6, 0.7, 1
                size_hint_y: None
                height: 20
                text_size: self.size
                halign: 'left'
            Spinner:
                id: file_spinner
                text: root.initial_zip
                values: root.zip_files
                font_size: '16sp'
                background_normal: ''
                background_color: 0, 0, 0, 0  # डिफ़ॉल्ट बटन लुक गायब
                color: 1, 1, 1, 1

        # कार्ड 2: कैरेक्टर सेट
        BoxLayout:
            orientation: 'vertical'
            padding: [15, 10, 15, 10]
            canvas.before:
                Color:
                    rgba: 0.08, 0.1, 0.15, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [12]
            Label:
                text: "⚙️ पासवर्ड का प्रकार (Character Set)"
                font_size: '13sp'
                color: 0.5, 0.6, 0.7, 1
                size_hint_y: None
                height: 20
                text_size: self.size
                halign: 'left'
            Spinner:
                id: char_spinner
                text: "Numbers (0-9)"
                values: ["Capital Letters (A-Z)", "Small Letters (a-z)", "Numbers (0-9)", "Alphanumeric (Mix)"]
                font_size: '16sp'
                background_normal: ''
                background_color: 0, 0, 0, 0
                color: 1, 1, 1, 1

        # कार्ड 3: पासवर्ड की लंबाई
        BoxLayout:
            orientation: 'vertical'
            padding: [15, 10, 15, 10]
            canvas.before:
                Color:
                    rgba: 0.08, 0.1, 0.15, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [12]
            Label:
                text: "🔢 पासवर्ड की लंबाई दर्ज करें"
                font_size: '13sp'
                color: 0.5, 0.6, 0.7, 1
                size_hint_y: None
                height: 20
                text_size: self.size
                halign: 'left'
            TextInput:
                id: length_input
                text: "4"
                multiline: False
                input_filter: 'int'
                font_size: '18sp'
                background_normal: ''
                background_color: 0, 0, 0, 0  # बॉर्डरलेस इनपुट
                foreground_color: 1, 1, 1, 1
                cursor_color: 0, 1, 0.8, 1
                padding: [0, 5, 0, 0]

    # लाइव टर्मिनल/कंसोल (यह एकदम हैकर वाइब देगा)
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        canvas.before:
            Color:
                rgba: 0.02, 0.03, 0.04, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [16]
            Color:
                rgba: 0, 1, 0.8, 0.2  # हल्का नियॉन बॉर्डर
            Line:
                rounded_rectangle: (self.x, self.y, self.width, self.height, 16)
                width: 1.2
        Label:
            id: status_label
            text: "STATUS: READY TO ATTACK"
            markup: True
            font_size: '16sp'
            halign: 'center'
            valign: 'middle'
            text_size: self.size
            color: 0, 1, 0.8, 1

    # फुल्ली कस्टम ग्लास-लुक स्टार्ट बटन
    Button:
        id: start_btn
        text: "START BRUTEFORCE"
        font_size: '18sp'
        font_bold: True
        size_hint_y: None
        height: 55
        background_normal: ''
        background_color: 0, 0, 0, 0  # पुराना बटन लुक पूरी तरह खत्म
        color: 0, 0, 0, 1  # डार्क टेक्स्ट नियॉन पर चमकेगा
        on_press: root.start_process()
        canvas.before:
            Color:
                rgba: (0, 1, 0.8, 1) if self.state == 'normal' else (0, 0.7, 0.6, 1)  # टच करने पर कलर चेंज
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [14]
''')

EXTRACT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_extract_temp")

class ZipCrackerLayout(BoxLayout):
    def __init__(self, **kwargs):
        self.zip_files = [f for f in os.listdir('.') if f.lower().endswith('.zip')]
        self.initial_zip = self.zip_files[0] if self.zip_files else "कोई ZIP फ़ाइल नहीं मिली"
        if not self.zip_files:
            self.zip_files = ["कोई ZIP फ़ाइल नहीं मिली"]
            
        super(ZipCrackerLayout, self).__init__(**kwargs)
        
        self.char_options = {
            "Capital Letters (A-Z)": [chr(i) for i in range(65, 91)],
            "Small Letters (a-z)": [chr(i) for i in range(97, 123)],
            "Numbers (0-9)": [chr(i) for i in range(48, 58)],
            "Alphanumeric (Mix)": [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)] + [chr(i) for i in range(48, 58)]
        }

    def update_status(self, text):
        self.ids.status_label.text = text

    def start_process(self):
        selected_zip = self.ids.file_spinner.text
        if selected_zip == "कोई ZIP फ़ाइल नहीं मिली" or not selected_zip.endswith('.zip'):
            self.update_status("[color=FF4444]❌ ERROR: NO VALID ZIP[/color]")
            return

        try:
            length = int(self.ids.length_input.text)
            if length <= 0: raise ValueError
        except ValueError:
            self.update_status("[color=FF4444]❌ ERROR: INVALID LENGTH[/color]")
            return

        self.ids.start_btn.disabled = True
        self.update_status("[color=FFFF00]⏳ CRACKING STARTED...[/color]")
        
        threading.Thread(target=self.secure_brute_logic, args=(selected_zip, length), daemon=True).start()

    def secure_brute_logic(self, zip_path, length):
        char_set_name = self.ids.char_spinner.text
        chars = self.char_options[char_set_name]
        
        start_time = time.time()
        attempts = 0
        found_password = None

        try:
            with pyzipper.AESZipFile(zip_path) as zf:
                for guess in itertools.product(chars, repeat=length):
                    pwd = "".join(guess)
                    attempts += 1
                    
                    if attempts % 300 == 0:
                        Clock.schedule_once(lambda dt, p=pwd: self.update_status(f"TRYING: [color=00FFCC]{p}[/color]"))
                    
                    zf.setpassword(pwd.encode('utf-8'))
                    try:
                        zf.testzip()
                        os.makedirs(EXTRACT_DIR, exist_ok=True)
                        zf.extractall(path=EXTRACT_DIR)
                        found_password = pwd
                        break
                    except (RuntimeError, pyzipper.BadZipFile):
                        continue
                        
            elapsed_time = time.time() - start_time
            if found_password:
                result_text = f"[color=00FF00]✅ SUCCESS!\nPASSWORD: [b]'{found_password}'[/b][/color]\n[color=888888]Time: {elapsed_time:.2f}s | Attempts: {attempts}[/color]"
            else:
                result_text = "[color=FF4444]❌ FAILED: NOT FOUND[/color]"
                
        except Exception as e:
            result_text = f"[color=FF4444]❌ ERROR: {str(e)}[/color]"
        finally:
            if os.path.exists(EXTRACT_DIR):
                shutil.rmtree(EXTRACT_DIR, ignore_errors=True)
            
            Clock.schedule_once(lambda dt: self.update_status(result_text))
            Clock.schedule_once(lambda dt: setattr(self.ids.start_btn, 'disabled', False))

class ZipCrackerApp(App):
    def build(self):
        self.title = "Zip Cracker Pro"
        return ZipCrackerLayout()

if __name__ == "__main__":
    ZipCrackerApp().run()
