import MetaTrader5 as mt5
import pandas as pd
from engines.atr import custom_atr
from engines.zigzag import calculate_zigzag

SYMBOL = "XAUUSDzero"
COUNT = 1000  # تعداد کندل برای محاسبه ATR(264)

if not mt5.initialize():
    print("❌ اتصال برقرار نشد:", mt5.last_error())
    quit()

# گرفتن کندل‌های M5
rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, COUNT)
mt5.shutdown()

if rates is None:
    print("❌ گرفتن کندل ناموفق:", mt5.last_error())
    quit()

# تبدیل به newest-first (قرارداد موتور ما)
df = pd.DataFrame(rates)
df = df.iloc[::-1].reset_index(drop=True)

candles = [
    {
        'time': int(row['time']),
        'open': float(row['open']),
        'high': float(row['high']),
        'low': float(row['low']),
        'close': float(row['close']),
    }
    for _, row in df.iterrows()
]

print(f"✅ {len(candles)} کندل M5 آماده شد")
print(f"   جدیدترین: {candles[0]['close']}  |  قدیمی‌ترین: {candles[-1]['close']}")
print()

# محاسبه ATR سفارشی
atr = custom_atr(candles, tf='M5')
print(f"✅ ATR محاسبه شد | ATR کندل آخر: {atr[0]:.4f}")
print()

# محاسبه ZigZag
pivots = calculate_zigzag(candles, atr)
print(f"✅ {len(pivots)} پیوت پیدا شد")
print()

print("=== ۱۰ پیوت آخر (جدیدترین اول) ===")
for p in pivots[:10]:
    kind = "HIGH" if p['is_high'] else "LOW "
    cand = " (کاندید)" if p['is_candidate'] else ""
    print(f"  {kind} | {p['price']:.2f} | {p['time']}{cand}")