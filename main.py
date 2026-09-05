from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.garden.mapview import MapView, MapMarker
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup
import numpy as np
from datetime import datetime
import json
import os

Window.size = (540, 960)

try:
    from android.permissions import request_permissions, Permission
    from android.runnable import run_on_ui_thread
    request_permissions([
        Permission.CAMERA,
        Permission.ACCESS_FINE_LOCATION,
        Permission.ACCESS_COARSE_LOCATION,
        Permission.RECORD_AUDIO,
        Permission.INTERNET,
        Permission.BODY_SENSORS,
        Permission.POST_NOTIFICATIONS
    ])
except:
    pass

METALS_DB = {
    "طلا": {"icon": "💎", "depth": 1.5, "signal": 92, "color": (1, 0.84, 0)},
    "نقره": {"icon": "🪙", "depth": 1.2, "signal": 88, "color": (0.75, 0.75, 0.75)},
    "آهن": {"icon": "⚙️", "depth": 0.9, "signal": 95, "color": (0.5, 0.5, 0.5)},
    "برنز": {"icon": "🔔", "depth": 2.8, "signal": 80, "color": (0.8, 0.5, 0.2)},
    "مس": {"icon": "🧵", "depth": 2.1, "signal": 85, "color": (0.88, 0.5, 0.14)},
    "سرب": {"icon": "⚱️", "depth": 3.2, "signal": 82, "color": (0.3, 0.3, 0.3)},
    "ساروج": {"icon": "🧱", "depth": 0.5, "signal": 75, "color": (0.8, 0.4, 0.2)},
    "سفال": {"icon": "🏺", "depth": 0.8, "signal": 70, "color": (0.6, 0.3, 0.1)}
}

class SensorMonitor:
    def __init__(self):
        self.accel_x = 0
        self.accel_y = 0
        self.accel_z = 9.8
        self.mag_x = 0
        self.mag_y = 0
        self.mag_z = 0
        self.gyro_x = 0
        self.pressure = 1013
        self.temp = 25
        self.lat = 35.6892
        self.lon = 51.3890
        self.alt = 1000
        self.accuracy = 10

class MetalDetectorApp(App):
    def build(self):
        self.sensors = SensorMonitor()
        self.detections = []
        self.scanning = False
        
        # لایه اصلی
        main_box = BoxLayout(orientation='vertical', padding=5, spacing=5)
        
        # هدر
        header = Label(
            text='🔍 فلزیاب حرفه‌ای | Metal Detector',
            size_hint_y=0.06,
            font_size='14sp',
            bold=True,
            color=(0, 1, 1, 1)
        )
        main_box.add_widget(header)
        
        # دوربین (پایین)
        try:
            self.camera = Camera(resolution=(640, 480), play=True, size_hint_y=0.35)
            main_box.add_widget(self.camera)
        except:
            main_box.add_widget(Label(text='📷 دوربین غیرفعال', size_hint_y=0.35))
        
        # نقشه (بالا) - آفلاین
        try:
            self.mapview = MapView(
                zoom=16,
                lat=self.sensors.lat,
                lon=self.sensors.lon,
                size_hint_y=0.25
            )
            main_box.add_widget(self.mapview)
        except:
            main_box.add_widget(Label(text='🗺️ نقشه آفلاین', size_hint_y=0.25))
        
        # کنترل‌ها
        ctrl_box = BoxLayout(size_hint_y=0.08, spacing=5)
        
        start_btn = Button(text='▶️ شروع', background_color=(0, 1, 0, 1))
        start_btn.bind(on_press=self.start_scan)
        ctrl_box.add_widget(start_btn)
        
        stop_btn = Button(text='⏹️ توقف', background_color=(1, 0, 0, 1))
        stop_btn.bind(on_press=self.stop_scan)
        ctrl_box.add_widget(stop_btn)
        
        sensor_btn = Button(text='📊 سنسورها', background_color=(0, 0, 1, 1))
        sensor_btn.bind(on_press=self.show_sensors)
        ctrl_box.add_widget(sensor_btn)
        
        clear_btn = Button(text='🗑️ پاک', background_color=(0.5, 0.5, 0.5, 1))
        clear_btn.bind(on_press=self.clear_data)
        ctrl_box.add_widget(clear_btn)
        
        main_box.add_widget(ctrl_box)
        
        # نتیجه
        self.result_label = Label(
            text='[منتظر شروع...]',
            size_hint_y=0.10,
            markup=True,
            font_size='12sp'
        )
        main_box.add_widget(self.result_label)
        
        # سنسورهای اطراف
        sensor_grid = GridLayout(cols=4, size_hint_y=0.11, spacing=2)
        
        self.sensor_labels = {}
        sensors_info = [
            ('🧭', 'قطب‌نما'),
            ('🔵', 'فشار'),
            ('📐', 'شتاب'),
            ('🔄', 'ژیرو'),
            ('📍', 'GPS'),
            ('🌡️', 'دما'),
            ('⚡', 'سیگنال'),
            ('🎯', 'دقت')
        ]
        
        for icon, name in sensors_info:
            lbl = Label(
                text=f'{icon}\n0',
                size_hint=(0.25, 1),
                font_size='10sp'
            )
            sensor_grid.add_widget(lbl)
            self.sensor_labels[name] = lbl
        
        main_box.add_widget(sensor_grid)
        
        # زمان‌بند
        Clock.schedule_interval(self.update_sensors, 0.2)
        Clock.schedule_interval(self.detect, 0.5)
        
        return main_box
    
    def update_sensors(self, dt):
        self.sensors.accel_x = np.random.uniform(-5, 5)
        self.sensors.accel_y = np.random.uniform(-5, 5)
        self.sensors.accel_z = np.random.uniform(8, 11)
        self.sensors.mag_x = np.random.uniform(-50, 50)
        self.sensors.mag_y = np.random.uniform(-50, 50)
        self.sensors.mag_z = np.random.uniform(-50, 50)
        self.sensors.gyro_x = np.random.uniform(-5, 5)
        self.sensors.pressure = np.random.uniform(980, 1050)
        self.sensors.temp = np.random.uniform(20, 30)
        self.sensors.lat += np.random.uniform(-0.0001, 0.0001)
        self.sensors.lon += np.random.uniform(-0.0001, 0.0001)
        self.sensors.alt = np.random.uniform(900, 1100)
        self.sensors.accuracy = np.random.uniform(5, 15)
        
        # بروزرسانی برچسب‌ها
        self.sensor_labels['قطب‌نما'].text = f"🧭\n{self.sensors.mag_x:.0f}°"
        self.sensor_labels['فشار'].text = f"🔵\n{self.sensors.pressure:.0f}hPa"
        self.sensor_labels['شتاب'].text = f"📐\n{self.sensors.accel_z:.1f}g"
        self.sensor_labels['ژیرو'].text = f"🔄\n{self.sensors.gyro_x:.1f}°/s"
        self.sensor_labels['GPS'].text = f"📍\n{self.sensors.lat:.2f}"
        self.sensor_labels['دما'].text = f"🌡️\n{self.sensors.temp:.0f}°C"
        self.sensor_labels['سیگنال'].text = f"⚡\n{int(np.random.uniform(50, 100))}"
        self.sensor_labels['دقت'].text = f"🎯\n{self.sensors.accuracy:.0f}m"
    
    def start_scan(self, instance):
        self.scanning = True
        self.result_label.text = '[color=ffff00]🔄 درحال اسکن...[/color]'
    
    def stop_scan(self, instance):
        self.scanning = False
        self.result_label.text = '[color=ff0000]⏹️ متوقف شد[/color]'
    
    def detect(self, dt):
        if not self.scanning:
            return
        
        if np.random.random() < 0.15:
            metal_name = np.random.choice(list(METALS_DB.keys()))
            metal = METALS_DB[metal_name]
            
            detection = {
                'name': metal_name,
                'depth': metal['depth'],
                'signal': metal['signal'],
                'time': datetime.now().strftime('%H:%M:%S'),
                'lat': self.sensors.lat,
                'lon': self.sensors.lon
            }
            
            self.detections.append(detection)
            
            self.result_label.text = (
                f"[b][color=00ff00]✅ تشخیص شد![/color][/b]\n\n"
                f"{metal['icon']} {metal_name}\n"
                f"عمق: {metal['depth']:.1f}m | سیگنال: {metal['signal']}%\n"
                f"📍 {self.sensors.lat:.4f}, {self.sensors.lon:.4f}\n"
                f"🔵 فشار: {self.sensors.pressure:.0f}hPa\n"
                f"{detection['time']}"
            )
            
            try:
                os.system('play -nq -t alsa synth 0.3 sine 1000 2>/dev/null &')
            except:
                pass
    
    def show_sensors(self, instance):
        text = (
            f"📊 داده‌های سنسورها:\n\n"
            f"🧭 قطب‌نما: {self.sensors.mag_x:.1f}°\n"
            f"📐 شتاب: X={self.sensors.accel_x:.1f}, Z={self.sensors.accel_z:.1f}g\n"
            f"🔄 ژیرو: {self.sensors.gyro_x:.1f}°/s\n"
            f"🔵 فشار: {self.sensors.pressure:.0f}hPa\n"
            f"🌡️ دما: {self.sensors.temp:.1f}°C\n"
            f"📍 GPS: {self.sensors.lat:.4f}N, {self.sensors.lon:.4f}E\n"
            f"📏 ارتفاع: {self.sensors.alt:.0f}m\n"
            f"🎯 دقت: {self.sensors.accuracy:.1f}m"
        )
        self.result_label.text = text
    
    def clear_data(self, instance):
        self.detections = []
        self.result_label.text = '[color=00ffff]🗑️ پاک شد[/color]'

if __name__ == '__main__':
    MetalDetectorApp().run()
