"""
Z-P-S | مانیتور پیوت در ترمینال
هر N ثانیه کندل‌ها رو می‌گیره، پیوت‌ها رو محاسبه می‌کنه،
و اگه پیوت جدید تأییدشده‌ای اضافه شد، اعلان می‌ده.
"""
import time
import argparse
from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
from engines.atr import custom_atr
from engines.zigzag import calculate_zigzag
from engines.classify import classify_pivots

# ===== تنظیمات پیش‌فرض =====
DEFAULT_SYMBOL = "XAUUSDzero"
DEFAULT_TF_NAME = "M5"
DEFAULT_SCAN_INTERVAL = 5
MAX_SCAN = 20
COUNT = 2000
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

def fetch_candles(symbol, tf_mt5, count):
    rates = mt5.copy_rates_from_pos(symbol, tf_mt5, 0, count)
    if rates is None:
        return None
    df = pd.DataFrame(rates).iloc[::-1].reset_index(drop=True)
    return [
        {'time': int(r['time']), 'open': float(r['open']), 'high': float(r['high']),
         'low': float(r['low']), 'close': float(r['close'])}
        for _, r in df.iterrows()
    ]

def format_pivot(p):
    kind = "HIGH ▲" if p['is_high'] else "LOW  ▼"
    ts = pd.to_datetime(p['time'], unit='s').strftime('%H:%M | %Y-%m-%d')
    return f"{kind}  @  {p['price']:.2f}   ({ts})"

def print_banner(symbol, tf_name, scan_interval):
    print("\033[96m" + "═" * 75)
    print("  🟢 Z-P-S | مانیتور پیوت")
    print("═" * 75)
    print(f"  نماد: {symbol}   |   تایم‌فریم: {tf_name}   |   فاصله چک: {scan_interval} ثانیه")
    print("  (برای توقف Ctrl+C را بزنید)")
    print("─" * 75 + "\033[0m\n")

def print_pivot_alert(p, classified_data=None):
    now = datetime.now().strftime('%H:%M:%S')
    kind = "HIGH ▲" if p['is_high'] else "LOW  ▼"
    ts = pd.to_datetime(p['time'], unit='s').strftime('%Y-%m-%d %H:%M')
    
    print("\033[93m" + "─" * 75)
    print(f"  🔔 پیوت جدید تأیید شد! (ساعت {now})")
    print(f"  نوع: {kind}   |   قیمت: {p['price']:.2f}   |   زمان: {ts}")
    
    if classified_data:
        c = classified_data
        print(f"  طبقه‌بندی: {c['type']}   |   l1pct: {c['l1pct']:.1f}%   |   l2pct: {c['l2pct']:.1f}%")
    
    print("─" * 75 + "\033[0m\n")

def main():
    parser = argparse.ArgumentParser(description="مانیتور زنده پیوت‌های Z-P-S")
    parser.add_argument("-s", "--symbol", type=str, default=DEFAULT_SYMBOL, help=f"نام نماد (پیش‌فرض: {DEFAULT_SYMBOL})")
    parser.add_argument("-t", "--tf", type=str, default=DEFAULT_TF_NAME, choices=TF_MAP.keys(), help=f"تایم‌فریم (پیش‌فرض: {DEFAULT_TF_NAME})")
    parser.add_argument("-i", "--interval", type=int, default=DEFAULT_SCAN_INTERVAL, help=f"فاصله چک کردن به ثانیه (پیش‌فرض: {DEFAULT_SCAN_INTERVAL})")
    args = parser.parse_args()

    symbol = args.symbol
    tf_name = args.tf
    tf_mt5 = TF_MAP[tf_name]
    scan_interval = args.interval

    if not mt5.initialize():
        print("❌ اتصال برقرار نشد:", mt5.last_error())
        return

    print_banner(symbol, tf_name, scan_interval)

    seen_confirmed = set()
    first_run = True

    try:
        while True:
            candles = fetch_candles(symbol, tf_mt5, COUNT)
            if candles is None:
                print(f"⚠️ خطا در گرفتن کندل: {mt5.last_error()}")
                time.sleep(scan_interval)
                continue

            atr = custom_atr(candles, tf=tf_name)
            pivots = calculate_zigzag(candles, atr)
            confirmed = [p for p in pivots if not p['is_candidate']]

            # در اجرای اول، همه رو «دیده‌شده» علامت بزن (اعلان نده)
            if first_run:
                for p in confirmed:
                    seen_confirmed.add((p['time'], p['price'], p['is_high']))
                
                print(f"\033[92m✅ شروع مانیتورینگ | {len(confirmed)} پیوت تأییدشده موجود\033[0m")
                if confirmed:
                    print(f"   آخرین پیوت ثبت‌شده: {format_pivot(confirmed[0])}")
                print("-" * 75 + "\n")
                first_run = False
                time.sleep(scan_interval)
                continue

            # پیوت‌های جدید
            new_pivots = [
                p for p in confirmed
                if (p['time'], p['price'], p['is_high']) not in seen_confirmed
            ]

            for p in new_pivots:
                seen_confirmed.add((p['time'], p['price'], p['is_high']))
                
                # پیدا کردن اطلاعات طبقه‌بندی
                classified = classify_pivots(pivots, candles, atr, max_scan=MAX_SCAN)
                p_class_data = None
                for c in classified:
                    if c['pivot']['time'] == p['time'] and c['pivot']['price'] == p['price']:
                        p_class_data = c
                        break
                
                print_pivot_alert(p, p_class_data)

            time.sleep(scan_interval)

    except KeyboardInterrupt:
        print("\n\033[90m⏹ متوقف شد.\033[0m")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()