```markdown
<div align="center">
  <h1>Z-P-S | ربات معامله‌گر چندموتوره</h1>
  <p>Strategy (استراتژی) | Setup (ستاپ) | Plan (پلن)</p>
  
  [![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/)
  [![MetaTrader 5](https://img.shields.io/badge/MetaTrader-5-success?logo=meta)](https://www.metatrader5.com/)
  [![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)](https://www.microsoft.com/windows)
  [![Status](https://img.shields.io/badge/Status-Strategy_Engine_Completed-orange)]()
</div>

---

## 📌 معرفی
**Z-P-S** یک سیستم معاملاتی الگوریتمی به زبان پایتون است که مستقیماً به ترمینال **MetaTrader 5** متصل می‌شود. معماری این پروژه بر پایه جداسازی سه بخش اصلی معامله‌گری بنا شده است:
1. **موتور استراتژی (Strategy):** تشخیص سطوح و پیوت‌های سفارشی.
2. **موتور ستاپ (Setup):** تشخیص سیگنال ورود (در حال توسعه).
3. **موتور پلن (Plan):** مدیریت ریسک و حجم (در حال توسعه).

---

## 🧠 موتور استراتژی (پیاده‌سازی شده)
منطق این بخش دقیقاً پورت شده از یک اندیکاتور اختصاصی MQL5 است.
- **ATR سفارشی:** محاسبه ترکیبی میانگین ATR های ۵۵، ۸۹ و ۲۶۴ دوره.
- **الگوریتم ZigZag:** تشخیص پیوت‌ها با تأییدیه ATR (دقیقاً مطابق اندیکاتور).
- **طبقه‌بندی پیوت:** تفکیک پیوت‌ها به ۴ نوع `Std` (استاندارد)، `Rev` (برگشتی)، `Trnd` (روند) و `Liq` (لیکوییدیشن).

---

## 📂 ساختار پروژه
```text
trading-bot/
├── engines/
│   ├── atr.py           # محاسبه ATR سفارشی
│   ├── zigzag.py        # الگوریتم پیوت‌یابی
│   └── classify.py      # طبقه‌بندی پیوت‌ها
├── show_last_pivots.py  # اسکریپت نمایش تاریخچه پیوت‌ها
├── pivot_monitor.py     # مانیتور زنده و اعلان در ترمینال
├── test_mt5_connection.py
├── test_pivot_mt5.py
└── test_pivot_check.py
```

---

## ⚙️ نصب و راه‌اندازی
**پیش‌نیازها:** ویندوز، پایتون 3.10+، متاتریدر 5 (باز و لاگین شده).

```cmd
# 1. ساخت محیط مجازی
python -m venv venv
venv\Scripts\activate

# 2. نصب پیش‌نیازها
pip install MetaTrader5 pandas python-dotenv
```

---

## 💻 دستورات اجرا

**نمایش پیوت‌های گذشته:**
```cmd
# نمایش 10 پیوت آخر طلا در تایم‌فریم 5 دقیقه
python show_last_pivots.py -s XAUUSDzero -t M5 -n 10

# پارامترها:
# -s : نماد (Symbol)
# -t : تایم‌فریم (M1, M5, M15, M30, H1, H4, D1)
# -n : تعداد پیوت‌های نمایشی
```

**مانیتور زنده بازار:**
```cmd
# چک کردن پیوت‌های جدید هر 5 ثانیه
python pivot_monitor.py -s XAUUSDzero -t M5 -i 5

# پارامترها:
# -i : فاصله چک کردن به ثانیه
# (برای خروج: Ctrl+C)
```

---

## 🗺️ نقشه راه
- [x] فاز ۱: پیاده‌سازی موتور استراتژی (ATR, ZigZag, Classification)
- [x] فاز ۲: اتصال به متاتریدر و سیستم اعلان ترمینال
- [ ] فاز ۳: پیاده‌سازی موتور ستاپ (شکست و خط موازی)
- [ ] فاز ۴: پیاده‌سازی موتور پلن (مدیریت ریسک)
- [ ] فاز ۵: اتصال به تلگرام و اجرای خودکار (Auto-Trading)

---

## ⚠️ سلب مسئولیت
این پروژه صرفاً برای اهداف آموزشی و پژوهشی توسعه یافته است. معامله در بازارهای مالی ریسک بالایی دارد و هیچ تضمینی برای سودآوری وجود ندارد. مسئولیت هرگونه استفاده از این کد بر عهده کاربر است. همیشه در حساب‌های دمو (Demo) تست کنید.
```
