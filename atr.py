"""
موتور ATR سفارشی Z-P-S
پیاده‌سازی دقیق منطق TrexCalculator.mqh

قرارداد: candles[0] = جدیدترین، candles[-1] = قدیمی‌ترین
"""


def _true_range(candles):
    """محاسبه True Range برای هر کندل."""
    n = len(candles)
    tr = [0.0] * n
    for i in range(n):
        h = candles[i]['high']
        l = candles[i]['low']
        if i == n - 1:  # قدیمی‌ترین کندل، close قبلی نداریم
            tr[i] = h - l
        else:
            prev_close = candles[i + 1]['close']
            tr[i] = max(h - l, abs(h - prev_close), abs(l - prev_close))
    return tr


def _wilder_atr(candles, period):
    """
    ATR به روش متاتریدر (iATR).
    متاتریدر از میانگین ساده‌ی TR در N کندل آخر استفاده می‌کند.
    """
    n = len(candles)
    atr = [0.0] * n
    if n == 0 or period <= 0 or n < period:
        return atr

    tr = _true_range(candles)

    # برای هر کندل، میانگین ساده TR در period کندل آینده (قدیمی‌تر) را حساب کن
    for i in range(n - period, -1, -1):
        s = 0.0
        for j in range(i, i + period):
            s += tr[j]
        atr[i] = s / period

    return atr


def custom_atr(candles, tf=None):
    """
    ATR سفارشی Z-P-S:
      - W1:  (ATR22×1.028 + ATR55 + ATR89 + ATR178×0.94) / 4
      - MN1: (ATR24×1.01  + ATR55×0.97 + ATR89×0.93) / 3
      - سایر TFها: (ATR55 + ATR89 + ATR264) / 3
      - fallback: ATR14 (وقتی کندل کافی برای فرمول اصلی نیست)
    """
    n = len(candles)
    atr14 = _wilder_atr(candles, 14)

    if tf == 'W1':
        a22 = _wilder_atr(candles, 22)
        a55 = _wilder_atr(candles, 55)
        a89 = _wilder_atr(candles, 89)
        a178 = _wilder_atr(candles, 178)
        result = [0.0] * n
        for i in range(n):
            if n > 178 + i and a22[i] > 0 and a55[i] > 0 and a89[i] > 0 and a178[i] > 0:
                result[i] = (a22[i] * 1.028 + a55[i] + a89[i] + a178[i] * 0.94) / 4.0
            else:
                result[i] = atr14[i]
        return result

    if tf == 'MN1':
        a24 = _wilder_atr(candles, 24)
        a55 = _wilder_atr(candles, 55)
        a89 = _wilder_atr(candles, 89)
        result = [0.0] * n
        for i in range(n):
            if n > 89 + i and a24[i] > 0 and a55[i] > 0 and a89[i] > 0:
                result[i] = (a24[i] * 1.01 + a55[i] * 0.97 + a89[i] * 0.93) / 3.0
            else:
                result[i] = atr14[i]
        return result

    # حالت استاندارد (M5، M15، H1، ...)
    a55 = _wilder_atr(candles, 55)
    a89 = _wilder_atr(candles, 89)
    a264 = _wilder_atr(candles, 264)
    result = [0.0] * n
    for i in range(n):
        if n > 264 + i and a55[i] > 0 and a89[i] > 0 and a264[i] > 0:
            result[i] = (a55[i] + a89[i] + a264[i]) / 3.0
        else:
            result[i] = atr14[i]
    return result