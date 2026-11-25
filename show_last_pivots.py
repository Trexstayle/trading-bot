import argparse
import MetaTrader5 as mt5
import pandas as pd
from engines.atr import custom_atr
from engines.zigzag import calculate_zigzag
from engines.classify import classify_pivots

# ===== تنظیمات پیش‌فرض =====
DEFAULT_SYMBOL = "XAUUSDzero"
DEFAULT_TF_NAME = "M5"
DEFAULT_COUNT_PIVOTS = 10
COUNT_CANDLES = 2000  # برای اطمینان از پیدا شدن پیوت‌های کافی، کندل بیشتری می‌گیریم
# ===========================

# نقشه تایم‌فریم‌ها
TF_MAP = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}

def main():
    parser = argparse.ArgumentParser(description="نمایش پیوت‌های طبقه‌بندی‌شده Z-P-S")
    parser.add_argument("-s", "--symbol", type=str, default=DEFAULT_SYMBOL, help="نام نماد (پیش‌فرض: XAUUSDzero)")
    parser.add_argument("-t", "--tf", type=str, default=DEFAULT_TF_NAME, choices=TF_MAP.keys(), help="تایم‌فریم (پیش‌فرض: M5)")
    parser.add_argument("-n", "--num", type=int, default=DEFAULT_COUNT_PIVOTS, help="تعداد پیوت‌های نمایشی (پیش‌فرض: 10)")
    args = parser.parse_args()

    symbol = args.symbol
    tf_name = args.tf
    num_pivots = args.num
    tf_mt5 = TF_MAP[tf_name]

    # اتصال
    if not mt5.initialize():
        print("❌ اتصال برقرار نشد:", mt5.last_error())
        quit()

    rates = mt5.copy_rates_from_pos(symbol, tf_mt5, 0, COUNT_CANDLES)
    mt5.shutdown()

    if rates is None:
        print(f"❌ گرفتن کندل ناموفق (نماد: {symbol}):", mt5.last_error())
        quit()

    # تبدیل به newest-first
    df = pd.DataFrame(rates).iloc[::-1].reset_index(drop=True)
    candles = [
        {'time': int(r['time']), 'open': float(r['open']), 'high': float(r['high']),
         'low': float(r['low']), 'close': float(r['close'])}
        for _, r in df.iterrows()
    ]

    # محاسبه
    atr = custom_atr(candles, tf=tf_name)
    pivots = calculate_zigzag(candles, atr)
    
    # برای پیدا کردن تعداد دلخواه پیوت طبقه‌بندی شده، اسکن رو بیشتر می‌کنیم
    classified = classify_pivots(pivots, candles, atr, max_scan=100) 

    # ===== بنر =====
    print("\033[96m" + "═" * 75)
    print(f"  📊 {num_pivots} پیوت طبقه‌بندی‌شده آخر | {symbol} - {tf_name}")
    print("═" * 75)
    print(f"  کل کندل‌ها: {len(candles)}   |   کل پیوت‌ها: {len(pivots)}   |   طبقه‌بندی‌شده: {len(classified)}")
    print("─" * 75 + "\033[0m\n")

    # نمایش پیوت‌های درخواستی
    last_pivots = classified[:num_pivots] 

    if not last_pivots:
        print("\033[91m⚠️ هیچ پیوت طبقه‌بندی‌شده‌ای پیدا نشد\033[0m")
    else:
        for idx, c in enumerate(last_pivots, 1):
            p = c['pivot']
            kind = "HIGH ▲" if p['is_high'] else "LOW  ▼"
            cand = " (کاندید)" if p['is_candidate'] else ""
            ts = pd.to_datetime(p['time'], unit='s').strftime('%Y-%m-%d %H:%M')
            
            # رنگ‌بندی بر اساس نوع پیوت
            color = "\033[92m" if c['type'] == 'Std' else \
                    "\033[93m" if c['type'] == 'Rev' else \
                    "\033[94m" if c['type'] == 'Trnd' else "\033[95m" # Liq
            
            print(f"\033[90m[{idx:02d}]\033[0m {color}نوع: {c['type']:<5}\033[0m | "
                  f"{kind:<7}{cand} | "
                  f"قیمت: \033[1m{p['price']:.2f}\033[0m | "
                  f"زمان: {ts}")
            print(f"      l1pct: {c['l1pct']:>6.1f}% | l2pct: {c['l2pct']:>6.1f}% | "
                  f"has_close: {str(c['has_close']):<5} | ATR: {c['atr']:.4f}")
            print("\033[90m" + "─" * 75 + "\033[0m")

if __name__ == "__main__":
    main()