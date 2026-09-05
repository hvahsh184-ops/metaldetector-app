[app]
title = Metal Detector
package.name = metaldetector
package.domain = org.metaldetector

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0
requirements = python3,kivy,numpy,android

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# تمام مجوزهای لازم - خودکار فعال
android.permissions = CAMERA,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,RECORD_AUDIO,INTERNET,ACCESS_NETWORK_STATE,MODIFY_AUDIO_SETTINGS,ACCESS_BACKGROUND_LOCATION,POST_NOTIFICATIONS,BODY_SENSORS

# تمام سنسورهای دستگاه
android.features = android.hardware.camera,android.hardware.camera.autofocus,android.hardware.location.gps,android.hardware.microphone,android.hardware.sensor.accelerometer,android.hardware.sensor.magnetometer,android.hardware.sensor.gyroscope,android.hardware.sensor.barometer,android.hardware.sensor.compass,android.hardware.sensor.proximity,android.hardware.sensor.light

# Manifest اضافی
android.manifest_additions = <uses-permission android:name="android.permission.CAMERA" /><uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" /><uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" /><uses-permission android:name="android.permission.RECORD_AUDIO" /><uses-permission android:name="android.permission.INTERNET" /><uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" /><uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" /><uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" /><uses-permission android:name="android.permission.POST_NOTIFICATIONS" /><uses-permission android:name="android.permission.BODY_SENSORS" />

[buildozer]
log_level = 2
warn_on_root = 1
