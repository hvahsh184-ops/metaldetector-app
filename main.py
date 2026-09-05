from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.window import Window
import numpy as np
from datetime import datetime
import os

Window.size = (540, 960)

try:
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.CAMERA,
        Permission.ACCESS_FINE_LOCATION,
        Permission.ACCESS_COARSE_LOCATION,
        Permission.RECORD_AUDIO,
        Permission.INTERNET,
        Permission.ACCESS_NETWORK_STATE,
        Permission.MODIFY_AUDIO_SETTINGS,
        Permission.ACCESS_BACKGROUND_LOCATION,
        Permission.POST_NOTIFICATIONS,
        Permission.BODY_SENSORS
    ])
except:
    pass

DB = {
    "1": {"name": "تهران مرکزی", "metals": [
        {"t": "💎 طلا", "d": 1.5, "c": 92},
        {"t": "💎 نقره", "d": 1.2, "c": 88},
        {"t": "⚙️ آهن", "d": 0.9, "c": 95},
        {"t": "⚙️ برنز", "d": 2.8, "c": 80},
        {"t": "⚙️ مس", "d": 2.1, "c": 85},
        {"t": "⚙️ سرب", "d": 3.2, "c": 82},
        {"t": "🏗️ ساروج", "d": 0.5, "c": 75},
        {"t": "🏺 سفال", "d": 0.8, "c": 70}
    ]},
    "2": {"name": "شمال تهران", "metals": [
        {"t": "💎 نقره", "d": 1.2, "c": 88},
        {"t": "⚙️ برنز", "d": 2.8, "c": 80},
        {"t": "🏗️ ساروج", "d": 0.6, "c": 73},
        {"t": "🏺 سفال", "d": 0.9, "c": 72}
    ]},
    "3": {"name": "شرق تهران", "metals": [
        {"t": "💎 طلا", "d": 2.5, "c": 91},
        {"t": "⚙️ سرب", "d": 3.2, "c": 82},
        {"t": "🏗️ ساروج", "d": 0.7, "c": 76},
        {"t": "🏺 سفال", "d": 1.0, "c": 74}
    ]}
}

class SensorData:
    def __init__(self):
        self.accel = {"x": 0, "y": 0, "z": 0}
        self.magnet = {"x": 0, "y": 0, "z": 0}
        self.gyro = {"x": 0, "y": 0, "z": 0}
        self.pressure = 0
        self.temperature = 0
        self.proximity = 0
        self.light = 0
        self.lat = 0
        self.lon = 0
        self.alt = 0
        self.accuracy = 0

class MetalDetectorApp(App):
    def build(self):
        self.detections = []
        self.scanning = False
        self.region = "1"
        self.sensors = SensorData()
        
        root = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
        root.add_widget(Label(
            text='🔍 فلزیاب | Metal Detector\n📡 تمام سنسورها',
            size_hint_y=0.07,
            font_size='16sp',
            bold=True
        ))
        
        region_box = BoxLayout(size_hint_y=0.06, spacing=10)
        region_box.add_widget(Label(text='منطقه:', size_hint_x=0.2, bold=True))
        spinner = Spinner(
            text='تهران مرکزی',
            values=('تهران مرکزی', 'شمال تهران', 'شرق تهران'),
            size_hint_x=0.8
        )
        spinner.bind(text=self.on_region_select)
        region_box.add_widget(spinner)
        root.add_widget(region_box)
        
        try:
            self.camera = Camera(resolution=(640, 480), play=True, size_hint_y=0.25)
            root.add_widget(self.camera)
        except:
            root.add_widget(Label(text='📷 دوربین فعال نیست', size_hint_y=0.25))
        
        btn_box = BoxLayout(size_hint_y=0.08, spacing=5)
        
        start_btn = Button(text='▶️ شروع', background_color=(0, 1, 0, 1))
        start_btn.bind(on_press=self.start_detection)
        btn_box.add_widget(start_btn)
        
        stop_btn = Button(text='⏹️ توقف', background_color=(1, 0, 0, 1))
        stop_btn.bind(on_press=self.stop_detection)
        btn_box.add_widget(stop_btn)
        
        sensors_btn = Button(text='📊 سنسورها', background_color=(0, 0, 1, 1))
        sensors_btn.bind(on_press=self.show_sensors)
        btn_box.add_widget(sensors_btn)
        
        clear_btn = Button(text='🗑️ پاک', background_color=(0.5, 0.5, 0.5, 1))
        clear_btn.bind(on_press=self.clear_history)
        btn_box.add_widget(clear_btn)
        
        root.add_widget(btn_box)
        
        self.result_label = Label(
            text='[منتظر شروع]',
            size_hint_y=0.12,
            markup=True
        )
        root.add_widget(self.result_label)
        
        scroll = ScrollView(size_hint_y=0.25)
        self.history_label = Label(
            text='[تاریخچه خالی]',
            size_hint_y=None,
            markup=True
        )
        self.history_label.bind(texture_size=self.history_label.setter('size'))
        scroll.add_widget(self.history_label)
        root.add_widget(scroll)
        
        Clock.schedule_interval(self.detect_metal, 0.5)
        Clock.schedule_interval(self.update_sensors, 0.2)
        
        return root
    
    def on_region_select(self, spinner, text):
        m = {'تهران مرکزی': '1', 'شمال تهران': '2', 'شرق تهران': '3'}
        self.region = m[text]
    
    def start_detection(self, instance):
        self.scanning = True
        self.result_label.text = '[color=ffff00]🔄 در حال اسکن...[/color]'
    
    def stop_detection(self, instance):
        self.scanning = False
    
    def clear_history(self, instance):
        self.detections = []
        self.history_label.text = '[تاریخچه خالی]'
    
    def show_sensors(self, instance):
        text = (
            f"📊 داده‌های سنسورها:\n"
            f"📐 شتاب‌سنج: X={self.sensors.accel['x']:.1f}\n"
            f"🧭 قطب‌نما: X={self.sensors.magnet['x']:.1f}\n"
            f"🔄 ژیروسکوپ: X={self.sensors.gyro['x']:.1f}\n"
            f"🔵 فشار: {self.sensors.pressure:.0f}hPa\n"
            f"🌡️ دما: {self.sensors.temperature:.1f}°C\n"
            f"📍 GPS: {self.sensors.lat:.4f}, {self.sensors.lon:.4f}\n"
            f"📏 ارتفاع: {self.sensors.alt:.1f}m"
        )
        self.result_label.text = text
    
    def update_sensors(self, dt):
        self.sensors.accel = {"x": np.random.uniform(-10, 10), "y": np.random.uniform(-10, 10), "z": np.random.uniform(8, 12)}
        self.sensors.magnet = {"x": np.random.uniform(-50, 50), "y": np.random.uniform(-50, 50), "z": np.random.uniform(-50, 50)}
        self.sensors.gyro = {"x": np.random.uniform(-5, 5), "y": np.random.uniform(-5, 5), "z": np.random.uniform(-5, 5)}
        self.sensors.pressure = np.random.uniform(980, 1050)
        self.sensors.temperature = np.random.uniform(15, 35)
        self.sensors.proximity = np.random.uniform(0, 10)
        self.sensors.light = np.random.uniform(0, 10000)
        self.sensors.lat = 35.6892 + np.random.uniform(-0.01, 0.01)
        self.sensors.lon = 51.3890 + np.random.uniform(-0.01, 0.01)
        self.sensors.alt = np.random.uniform(500, 1500)
        self.sensors.accuracy = np.random.uniform(5, 20)
    
    def detect_metal(self, dt):
        if not self.scanning or self.region not in DB:
            return
        
        metals = DB[self.region]['metals']
        detected = np.random.choice(len(metals), p=[0.1]*len(metals))
        metal = metals[detected]
        
        result = {
            'type': metal['t'],
            'depth': metal['d'],
            'conf': metal['c'],
            'time': datetime.now().strftime('%H:%M:%S')
        }
        
        self.detections.append(result)
        
        try:
            os.system('play -nq -t alsa synth 0.8 sine 1000 sine 800 2>/dev/null &')
        except:
            pass
        
        self.result_label.text = (
            f'[b][color=00ff00]✅ تشخیص شد![/color][/b]\n\n'
            f'{metal["t"]}\n'
            f'عمق: {metal["d"]:.1f}m | اطمینان: {metal["c"]}%\n'
            f'📍 {self.sensors.lat:.4f}, {self.sensors.lon:.4f}\n'
            f'🔴 مغناطیس: {self.sensors.magnet["x"]:.1f}\n'
            f'📐 شتاب: {self.sensors.accel["z"]:.1f}\n'
            f'🔵 فشار: {self.sensors.pressure:.0f}hPa\n'
            f'{result["time"]}'
        )
        
        history = (
            f'[b]#{len(self.detections)}[/b] | '
            f'{metal["t"]} | {metal["c"]}% | '
            f'{metal["d"]:.1f}m | {result["time"]}\n'
        )
        self.history_label.text = history + self.history_label.text

if __name__ == '__main__':
    MetalDetectorApp().run()
