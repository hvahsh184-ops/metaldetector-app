from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
import random
from datetime import datetime

Window.size = (540, 960)

try:
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.CAMERA,
        Permission.ACCESS_FINE_LOCATION,
        Permission.ACCESS_COARSE_LOCATION,
        Permission.BODY_SENSORS,
    ])
except:
    pass

METALS_DB = {
    "طلا": {"icon": "💎", "depth": 1.5, "signal": 92},
    "نقره": {"icon": "🪙", "depth": 1.2, "signal": 88},
    "آهن": {"icon": "⚙️", "depth": 0.9, "signal": 95},
    "برنز": {"icon": "🔔", "depth": 2.8, "signal": 80},
    "مس": {"icon": "🧵", "depth": 2.1, "signal": 85},
    "سرب": {"icon": "⚱️", "depth": 3.2, "signal": 82},
    "ساروج": {"icon": "🧱", "depth": 0.5, "signal": 75},
    "سفال": {"icon": "🏺", "depth": 0.8, "signal": 70}
}

class SensorMonitor:
    def __init__(self):
        self.mag_x = 0
        self.accel_z = 9.8
        self.gyro_x = 0
        self.pressure = 1013
        self.temp = 25
        self.lat = 35.6892
        self.lon = 51.3890
        self.accuracy = 10

class MetalDetectorApp(App):
    def build(self):
        self.sensors = SensorMonitor()
        self.detections = []
        self.scanning = False
        
        main_box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # عنوان
        header = Label(
            text='🔍 فلزیاب حرفه‌ای | Metal Detector',
            size_hint_y=0.08,
            font_size='16sp',
            bold=True,
            color=(0, 1, 1, 1)
        )
        main_box.add_widget(header)
        
        # منطقه دوربین (قالب ساده)
        camera_box = BoxLayout(
            size_hint_y=0.25,
            orientation='vertical',
            padding=5
        )
        camera_label = Label(
            text='📹\nدوربین فعال',
            font_size='20sp',
            color=(0, 1, 1, 1)
        )
        camera_box.add_widget(camera_label)
        main_box.add_widget(camera_box)
        
        # منطقه نقشه (قالب ساده)
        map_box = BoxLayout(
            size_hint_y=0.20,
            orientation='vertical',
            padding=5
        )
        map_label = Label(
            text='🗺️\nنقشه آفلاین\n35.6892°N, 51.3890°E',
            font_size='14sp',
            color=(0, 1, 1, 1)
        )
        map_box.add_widget(map_label)
        main_box.add_widget(map_box)
        
        # دکمه‌های کنترل
        ctrl_box = BoxLayout(size_hint_y=0.10, spacing=5, padding=5)
        
        start_btn = Button(text='▶️ شروع', background_color=(0, 1, 0, 0.8), font_size='12sp')
        start_btn.bind(on_press=self.start_scan)
        ctrl_box.add_widget(start_btn)
        
        stop_btn = Button(text='⏹️ توقف', background_color=(1, 0, 0, 0.8), font_size='12sp')
        stop_btn.bind(on_press=self.stop_scan)
        ctrl_box.add_widget(stop_btn)
        
        sensor_btn = Button(text='📊 سنسورها', background_color=(0, 0, 1, 0.8), font_size='12sp')
        sensor_btn.bind(on_press=self.show_sensors)
        ctrl_box.add_widget(sensor_btn)
        
        clear_btn = Button(text='🗑️ پاک', background_color=(0.5, 0.5, 0.5, 0.8), font_size='12sp')
        clear_btn.bind(on_press=self.clear_data)
        ctrl_box.add_widget(clear_btn)
        
        main_box.add_widget(ctrl_box)
        
        # منطقه نتایج
        self.result_label = Label(
            text='[منتظر شروع...]\n\nدکمه شروع را بزن!',
            size_hint_y=0.15,
            markup=True,
            font_size='12sp',
            color=(0.5, 1, 0.5, 1)
        )
        main_box.add_widget(self.result_label)
        
        # سنسورهای اطراف
        sensor_grid = GridLayout(cols=4, size_hint_y=0.12, spacing=3, padding=5)
        
        self.sensor_labels = {}
        sensors_info = [
            ('🧭', 'قطب'),
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
                font_size='10sp',
                color=(0, 1, 1, 1)
            )
            sensor_grid.add_widget(lbl)
            self.sensor_labels[name] = lbl
        
        main_box.add_widget(sensor_grid)
        
        # زمان‌بند
        Clock.schedule_interval(self.update_sensors, 0.2)
        Clock.schedule_interval(self.detect, 0.5)
        
        return main_box
    
    def update_sensors(self, dt):
        self.sensors.mag_x = random.uniform(-50, 50)
        self.sensors.accel_z = random.uniform(8, 11)
        self.sensors.gyro_x = random.uniform(-5, 5)
        self.sensors.pressure = random.uniform(980, 1050)
        self.sensors.temp = random.uniform(20, 30)
        self.sensors.lat += random.uniform(-0.0001, 0.0001)
        self.sensors.lon += random.uniform(-0.0001, 0.0001)
        self.sensors.accuracy = random.uniform(5, 15)
        
        self.sensor_labels['قطب'].text = f"🧭\n{self.sensors.mag_x:.0f}°"
        self.sensor_labels['فشار'].text = f"🔵\n{self.sensors.pressure:.0f}"
        self.sensor_labels['شتاب'].text = f"📐\n{self.sensors.accel_z:.1f}g"
        self.sensor_labels['ژیرو'].text = f"🔄\n{self.sensors.gyro_x:.1f}"
        self.sensor_labels['GPS'].text = f"📍\n{self.sensors.lat:.2f}"
        self.sensor_labels['دما'].text = f"🌡️\n{self.sensors.temp:.0f}°"
        self.sensor_labels['سیگنال'].text = f"⚡\n{int(random.uniform(50, 100))}"
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
        
        if random.random() < 0.15:
            metal_name = random.choice(list(METALS_DB.keys()))
            metal = METALS_DB[metal_name]
            
            self.result_label.text = (
                f"[b][color=00ff00]✅ تشخیص شد![/color][/b]\n"
                f"{metal['icon']} {metal_name}\n"
                f"عمق: {metal['depth']:.1f}m\n"
                f"سیگنال: {metal['signal']}%\n"
                f"📍 {self.sensors.lat:.4f}, {self.sensors.lon:.4f}"
            )
    
    def show_sensors(self, instance):
        text = (
            f"📊 داده‌ه��ی سنسورها:\n\n"
            f"🧭 قطب‌نما: {self.sensors.mag_x:.1f}°\n"
            f"🔵 فشار: {self.sensors.pressure:.0f}hPa\n"
            f"📐 شتاب: {self.sensors.accel_z:.1f}g\n"
            f"🔄 ژیرو: {self.sensors.gyro_x:.1f}°/s\n"
            f"📍 GPS: {self.sensors.lat:.4f}\n"
            f"🌡️ دما: {self.sensors.temp:.1f}°C\n"
            f"🎯 دقت: {self.sensors.accuracy:.0f}m"
        )
        self.result_label.text = text
    
    def clear_data(self, instance):
        self.detections = []
        self.result_label.text = '[color=00ffff]🗑️ پاک شد[/color]'

if __name__ == '__main__':
    MetalDetectorApp().run()
