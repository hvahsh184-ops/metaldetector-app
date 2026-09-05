#!/bin/bash
# ساخت APK سریع

echo "🔨 شروع ساخت APK..."

# نصب ابزارهای لازم
apt-get update -qq
apt-get install -y -qq openjdk-11-jdk android-sdk android-ndk

# دانلود buildozer
pip install -q buildozer cython

# ساخت APK
cd /tmp/metaldetector
buildozer android release

# کپی APK
if [ -f "bin/metaldetector-1.0.0-release-unsigned.apk" ]; then
  cp bin/metaldetector-1.0.0-release-unsigned.apk metaldetector.apk
  echo "✅ APK آماده!"
else
  echo "❌ خطا در ساخت"
fi
