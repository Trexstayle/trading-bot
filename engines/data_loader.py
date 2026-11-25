"""
خواندن داده کندل از فایل CSV متاتریدر
"""

import csv
from datetime import datetime


def load_mt5_csv(file_path):
    """
    خواندن فایل CSV خروجی متاتریدر.
    ساختار فایل: time, open, high, low, close  (کاما-جدا)
    
    این تابع ترتیب را بر اساس تاریخ تشخیص می‌دهد، نه بر اساس فرض.
    خروجی همیشه جدیدترین-اول است.
    """
    candles = []

    with open(file_path, 'r', encoding='utf-8') as f:
        header = f.readline()  # رد کردن هدر

        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) < 5:
                continue
            try:
                candle = {
                    'datetime': parts[0].strip(),
                    'open': float(parts[1]),
                    'high': float(parts[2]),
                    'low': float(parts[3]),
                    'close': float(parts[4]),
                }
                candles.append(candle)
            except (ValueError, IndexError):
                continue

    # تشخیص ترتیب بر اساس تاریخ اولین و آخرین کندل
    if len(candles) >= 2:
        if candles[0]['datetime'] < candles[-1]['datetime']:
            # قدیمی‌ترین اول است → برعکس کن
            candles.reverse()
        # else: جدیدترین اول است → همانطور بگذار

    return candles
