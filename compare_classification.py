"""
مقایسه طبقه‌بندی پیوت‌ها بین پایتون و متاتریدر
"""
from engines.data_loader import load_mt5_csv
from engines.atr import custom_atr
from engines.zigzag import calculate_zigzag
from engines.pivot_classifier import classify_pivots


def load_mt5_pivots_with_type(file_path):
    """خواندن پیوت‌های متاتریدر با ستون pivot_type"""
    pivots = []
    with open(file_path, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) < 6:
                continue
            try:
                pivots.append({
                    'time': parts[0].strip().replace('.', '-'),
                    'price': float(parts[1]),
                    'index': int(parts[2]),
                    'is_high': parts[3].strip() == '1',
                    'is_candidate': parts[4].strip() == '1',
                    'pivot_type': parts[5].strip(),
                })
            except (ValueError, IndexError):
                continue
    return pivots


# بارگذاری داده
candles = load_mt5_csv('data/candles_export.csv')
for c in candles:
    c['time'] = c['datetime']

atr = custom_atr(candles, tf='M5')
zz = calculate_zigzag(candles, atr, atr_multiplier=1.0)
py_classified = classify_pivots(zz, candles, atr, max_scan=100)

mt5_pivots = load_mt5_pivots_with_type('data/pivots_export.csv')

# ساخت دیکشنری از طبقه‌بندی پایتون با کلید (زمان، قیمت)
py_map = {}
for c in py_classified:
    # زمان پایتون: 2026.11.23 09:00:00 → 2026-11-23 09:00:00
    py_time = c['pivot']['time'].replace('.', '-')
    key = (py_time, round(c['pivot']['price'], 2))
    py_map[key] = c['type']
# ساخت دیکشنری از طبقه‌بندی متاتریدر
mt5_map = {}
for p in mt5_pivots:
    if p['pivot_type'] != '':
        key = (p['time'], round(p['price'], 2))
        mt5_map[key] = p['pivot_type']

print(f"=== طبقه‌بندی ===")
print(f"پایتون: {len(py_map)} پیوت طبقه‌بندی‌شده")
print(f"متاتریدر: {len(mt5_map)} پیوت طبقه‌بندی‌شده")
print()
print("\n=== ۵ کلید اول پایتون ===")
for k in list(py_map.keys())[:5]:
    print(f"  {repr(k)}")

print("\n=== ۵ کلید اول متاتریدر ===")
for k in list(mt5_map.keys())[:5]:
    print(f"  {repr(k)}")
# مقایسه
common = set(py_map.keys()) & set(mt5_map.keys())
only_py = set(py_map.keys()) - set(mt5_map.keys())
only_mt5 = set(mt5_map.keys()) - set(py_map.keys())

print(f"✅ مشترک: {len(common)}")
print(f"❌ فقط پایتون: {len(only_py)}")
print(f"❌ فقط متاتریدر: {len(only_mt5)}")
print()

# بررسی نوع در مشترک‌ها
type_errors = 0
for k in sorted(common):
    py_type = py_map[k]
    mt5_type = mt5_map[k]
    if py_type != mt5_type:
        type_errors += 1
        print(f"⚠️ اختلاف نوع: {k[0]} price={k[1]}  پایتون={py_type}  متاتریدر={mt5_type}")

if type_errors == 0 and len(only_py) == 0 and len(only_mt5) == 0:
    print("🎉 عالی! طبقه‌بندی دقیقاً یکسان است")
elif type_errors == 0:
    print(f"⚠️ نوع‌ها یکسان هستند ولی برخی پیوت‌ها در یک طرف طبقه‌بندی نشده‌اند")

# نمایش جزئیات
print("\n=== جزئیات مشترک ===")
print(f"{'زمان':<22} | {'قیمت':>10} | {'پایتون':<6} | {'متاتریدر':<6}")
print("-" * 60)
for k in sorted(common):
    print(f"{k[0]:<22} | {k[1]:>10.2f} | {py_map[k]:<6} | {mt5_map[k]:<6}")