"""
مقایسه پیوت‌های پایتون با پیوت‌های اندیکاتور متاتریدر
ساختار فایل متاتریدر: کاما-جدا با ستون‌های:
  time, price, index, is_high, is_candidate
"""
from engines.data_loader import load_mt5_csv
from engines.atr import custom_atr
from engines.zigzag import calculate_zigzag


def load_mt5_pivots(file_path):
    """خواندن فایل پیوت‌های اندیکاتور (کاما-جدا)"""
    pivots = []
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
                pivots.append({
                    'time': parts[0].strip(),
                    'price': float(parts[1]),
                    'index': int(parts[2]),
                    'is_high': parts[3].strip() == '1',
                    'is_candidate': parts[4].strip() == '1',
                })
            except (ValueError, IndexError):
                continue
    return pivots


def compare(mt5_pivots, py_pivots):
    print(f"\n=== مقایسه ===")
    print(f"تعداد پیوت متاتریدر: {len(mt5_pivots)}")
    print(f"تعداد پیوت پایتون:   {len(py_pivots)}")

    # هر دو طرف را به یک فرمت یکسان نرمال می‌کنیم: خط تیره
    mt5_map = {}
    for p in mt5_pivots:
        key = (p['time'].replace('.', '-').strip(), round(p['price'], 2))
        mt5_map[key] = p

    py_map = {}
    for p in py_pivots:
        key = (p['time'].replace('.', '-').strip(), round(p['price'], 2))
        py_map[key] = p

    common = set(mt5_map.keys()) & set(py_map.keys())
    only_mt5 = set(mt5_map.keys()) - set(py_map.keys())
    only_py = set(py_map.keys()) - set(mt5_map.keys())

    print(f"\n✅ پیوت‌های مشترک: {len(common)}")
    print(f"❌ فقط در متاتریدر: {len(only_mt5)}")
    print(f"❌ فقط در پایتون:   {len(only_py)}")

    if only_mt5:
        print("\n--- پیوت‌هایی که پایتون نداره ---")
        for k in sorted(only_mt5)[:10]:
            p = mt5_map[k]
            kind = "High" if p['is_high'] else "Low"
            print(f"  {k[0]}  price={k[1]}  [{kind}]")

    if only_py:
        print("\n--- پیوت‌هایی که متاتریدر نداره ---")
        for k in sorted(only_py)[:10]:
            print(f"  {k[0]}  price={k[1]}")

    if len(only_mt5) == 0 and len(only_py) == 0:
        print("\n🎉 عالی! همه پیوت‌ها دقیقاً یکی هستند")
    else:
        print(f"\n⚠️ اختلاف وجود داره")

    return len(common), len(mt5_pivots), len(py_pivots)


# ===== اجرا =====
print("=== بارگذاری داده ===")
candles = load_mt5_csv('data/candles_export.csv')
print(f"کندل‌ها: {len(candles)}")

# zigzag ما از 'time' استفاده می‌کند
for c in candles:
    c['time'] = c['datetime']

print("\n=== محاسبه ATR ===")
atr = custom_atr(candles, tf='M5')
print(f"ATR جدیدترین: {atr[0]:.4f}")

print("\n=== محاسبه ZigZag ===")
py_pivots = calculate_zigzag(candles, atr, atr_multiplier=1.0)
print(f"پیوت‌های پایتون: {len(py_pivots)}")

print("\n=== بارگذاری پیوت‌های متاتریدر ===")
mt5_pivots = load_mt5_pivots('data/pivots_export.csv')
print(f"پیوت‌های متاتریدر: {len(mt5_pivots)}")

compare(mt5_pivots, py_pivots)