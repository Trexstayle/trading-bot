import MetaTrader5 as mt5

# اتصال به متاتریدر
if not mt5.initialize():
    print("❌ اتصال به متاتریدر برقرار نشد")
    print("کد خطا:", mt5.last_error())
    quit()

print("✅ اتصال به متاتریدر برقرار شد")
print()

# اطلاعات حساب
account_info = mt5.account_info()
if account_info is not None:
    print("=== اطلاعات حساب ===")
    print(f"شماره حساب: {account_info.login}")
    print(f"سرور: {account_info.server}")
    print(f"شرکت: {account_info.company}")
    print(f"موجودی: {account_info.balance} {account_info.currency}")
    print()
else:
    print("⚠️ به حساب لاگین نیستی (فقط داده‌ی عمومی در دسترس است)")
    print()

# اطلاعات نماد
symbol = "XAUUSDzero"  # یا هر نمادی که در متاتریدر داری
symbol_info = mt5.symbol_info(symbol)
if symbol_info is None:
    print(f"❌ نماد {symbol} پیدا نشد")
    print("نمادهای موجود (چند مورد اول):")
    symbols = mt5.symbols_get()
    for s in symbols[:10]:
        print(f"  - {s.name}")
else:
    print(f"✅ نماد {symbol} پیدا شد")
    print(f"قیمت فعلی: Bid={symbol_info.bid}, Ask={symbol_info.ask}")
    print()

# گرفتن چند کندل آخر
rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 5)
if rates is not None:
    print("=== ۵ کندل آخر M5 ===")
    for r in rates:
        print(f"  {r['time']}  O={r['open']}  H={r['high']}  L={r['low']}  C={r['close']}")
else:
    print("❌ گرفتن کندل‌ها ناموفق بود")
    print("کد خطا:", mt5.last_error())

# بستن اتصال
mt5.shutdown()