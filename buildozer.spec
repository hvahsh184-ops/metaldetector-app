[app]
title = Metal Detector
package.name = metaldetector
package.domain = org.metaldetector

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0
requirements = python3,kivy,numpy,android

orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# مجوزهای کامل برای Android 13 و 14
android.permissions = CAMERA,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,RECORD_AUDIO,INTERNET,ACCESS_NETWORK_STATE,MODIFY_AUDIO_SETTINGS,ACCESS_BACKGROUND_LOCATION,POST_NOTIFICATIONS

# سنسورها
android.features = android.hardware.camera,android.hardware.camera.autofocus,android.hardware.location.gps,android.hardware.microphone,android.hardware.sensor.accelerometer,android.hardware.sensor.magnetometer,android.hardware.sensor.compass

# دسترسی‌های Runtime
android.gradle_dependencies = 
android.add_src = 

# Manifest اضافی
android.manifest_additions = <uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" /><uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

[buildozer]
log_level = 2
warn_on_root = 1
