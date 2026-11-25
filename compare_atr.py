"""
مقایسه ATR پایتون با ATR متاتریدر
"""
from engines.data_loader import load_mt5_csv
from engines.atr import custom_atr


def load_mt5_atr(file_path):
    """خواندن فایل ATR متاتریدر (ستون atr_custom)"""
    atrs = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) < 3:
                continue
            try:
                idx = int(parts[0])
                time = parts[1].strip()
                # اگر فایل جدید باشد (۷ ستون)، ستون آخر atr_custom است
                # اگر فایل قدیمی باشد (۳ ستون)، ستون سوم atr است
                if len(parts) >= 7:
                    atr_val = float(parts[6])
                else:
                    atr_val = float(parts[2])
                atrs[idx] = {'time': time, 'atr': atr_val}
            except (ValueError, IndexError):
                continue
    return atrs


# بارگذاری داده
candles = load_mt5_csv('data/candles_export.csv')
for c in candles:
    c['time'] = c['datetime']

# محاسبه ATR پایتون
py_atr = custom_atr(candles, tf='M5')

# بارگذاری ATR متاتریدر
mt5_atr = load_mt5_atr('data/atr_export.csv')

print(f"تعداد کندل CSV: {len(candles)}")
print(f"تعداد ATR متاتریدر: {len(mt5_atr)}")
print()

# === بررسی هم‌راستایی زمانی ===
print("=== بررسی هم‌راستایی زمانی ===")
print(f"جدیدترین کندل CSV: {candles[0]['datetime']}")
print(f"جدیدترین کندل MT5 (idx=0): {mt5_atr[0]['time'] if 0 in mt5_atr else 'N/A'}")
print(f"قدیمی‌ترین کندل CSV: {candles[-1]['datetime']}")
print(f"قدیمی‌ترین کندل MT5 (idx=499): {mt5_atr[499]['time'] if 499 in mt5_atr else 'N/A'}")
print()

# === مقایسه ATR ===
print("=== مقایسه ۵۰ کندل آخر ===")
print(f"{'idx':>4} | {'ATR پایتون':>12} | {'ATR متاتریدر':>12} | {'اختلاف':>10} | {'درصد':>8}")
print("-" * 65)

max_diff_pct = 0
for i in range(50):
    if i >= len(py_atr):
        break
    py = py_atr[i]
    mt5_data = mt5_atr.get(i)
    if mt5_data is None:
        continue
    mt5 = mt5_data['atr']
    diff = abs(py - mt5)
    diff_pct = (diff / mt5 * 100) if mt5 > 0 else 0
    max_diff_pct = max(max_diff_pct, diff_pct)
    if i < 20 or diff_pct > 0.01:
        print(f"{i:>4} | {py:>12.6f} | {mt5:>12.6f} | {diff:>10.6f} | {diff_pct:>7.4f}%")

print()
print(f"بیشترین اختلاف درصدی (۵۰ کندل آخر): {max_diff_pct:.6f}%")

if max_diff_pct < 0.0001:
    print("✅ ATR پایتون و متاتریدر کاملاً یکسان هستند")
elif max_diff_pct < 0.01:
    print("⚠️ ATR تقریباً یکسان است (اختلاف جزئی)")
elif max_diff_pct < 1.0:
    print("⚠️ ATR اختلاف کوچک دارد")
else:
    print("❌ ATR اختلاف جدی دارد — باید بررسی شود")