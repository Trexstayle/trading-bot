import MetaTrader5 as mt5
import pandas as pd
from engines.atr import custom_atr
from engines.zigzag import calculate_zigzag

SYMBOL = "XAUUSDzero"

mt5.initialize()
rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M5, 0, 1000)
mt5.shutdown()

df = pd.DataFrame(rates).iloc[::-1].reset_index(drop=True)
candles = [
    {'time': int(r['time']), 'open': float(r['open']), 'high': float(r['high']),
     'low': float(r['low']), 'close': float(r['close'])}
    for _, r in df.iterrows()
]

atr = custom_atr(candles, tf='M5')
pivots = calculate_zigzag(candles, atr)

# چک ۱: آیا دو پیوت متوالی هم‌جهت داریم؟ (نباید داشته باشیم)
errors_same_dir = 0
for i in range(len(pivots) - 1):
    if pivots[i]['is_high'] == pivots[i+1]['is_high']:
        errors_same_dir += 1
        print(f"⚠️ دو پیوت هم‌جهت: {pivots[i]} و {pivots[i+1]}")

# چک ۲: آیا HIGH و LOW روی یک timestamp داریم؟
errors_same_time = 0
for i in range(len(pivots) - 1):
    if pivots[i]['time'] == pivots[i+1]['time']:
        errors_same_time += 1
        print(f"⚠️ HIGH و LOW روی یک کندل: {pivots[i]['price']} / {pivots[i+1]['price']}")

# چک ۳: آیا HIGH واقعاً بالاتر از LOW بعده؟
errors_price = 0
for i in range(len(pivots) - 1):
    if pivots[i]['is_high'] and not pivots[i+1]['is_high']:
        if pivots[i]['price'] <= pivots[i+1]['price']:
            errors_price += 1

print(f"\n=== خلاصه ===")
print(f"کل پیوت‌ها: {len(pivots)}")
print(f"دو پیوت هم‌جهت متوالی: {errors_same_dir}")
print(f"HIGH و LOW روی یک کندل: {errors_same_time}")
print(f"HIGH پایین‌تر از LOW بعدی: {errors_price}")