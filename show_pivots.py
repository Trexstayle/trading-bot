"""
نمایش جزئیات پیوت‌های ZigZag با طبقه‌بندی
"""
from engines.data_loader import load_mt5_csv
from engines.atr import custom_atr
from engines.zigzag import calculate_zigzag
from engines.pivot_classifier import classify_pivots


# بارگذاری داده
candles = load_mt5_csv('data/candles_export.csv')
for c in candles:
    c['time'] = c['datetime']

# محاسبه ATR
atr = custom_atr(candles, tf='H1')

# محاسبه ZigZag
zz = calculate_zigzag(candles, atr, atr_multiplier=1.0)

print(f"=== تعداد پیوت‌ها: {len(zz)} ===\n")

# نمایش همه پیوت‌ها
print(f"{'شماره':>4} | {'زمان':<20} | {'قیمت':>10} | {'جهت':<6} | {'کاندید':<6} | {'ایندکس':>6}")
print("-" * 75)

for i, p in enumerate(zz):
    kind = "High" if p['is_high'] else "Low"
    cand = "بله" if p['is_candidate'] else "خیر"
    print(f"{i:>4} | {p['time']:<20} | {p['price']:>10.2f} | {kind:<6} | {cand:<6} | {p['index']:>6}")

# طبقه‌بندی
print("\n=== طبقه‌بندی پیوت‌ها ===")
classified = classify_pivots(zz, candles, atr, max_scan=100)
print(f"تعداد طبقه‌بندی‌شده: {len(classified)}\n")

print(f"{'شماره':>4} | {'نوع':<6} | {'جهت':<6} | {'قیمت':>10} | {'زمان':<20} | {'l1%':>8} | {'l2%':>8} | {'has_close':<10}")
print("-" * 95)

for i, c in enumerate(classified):
    kind = "High" if c['pivot']['is_high'] else "Low"
    close = "بله" if c['has_close'] else "خیر"
    print(f"{i:>4} | {c['type']:<6} | {kind:<6} | {c['pivot']['price']:>10.2f} | {c['pivot']['time']:<20} | {c['l1pct']:>8.1f} | {c['l2pct']:>8.1f} | {close:<10}")