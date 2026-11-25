"""
موتور طبقه‌بندی پیوت Z-P-S
پیاده‌سازی دقیق منطق DrawTrendLinesAndPivots از Pivot Trex.mq5

هر سه پیوت متوالی (P1, P2, P3) → P2 طبقه‌بندی می‌شه:
  - l1pct = فاصله P1→P2 به درصد ATR
  - l2pct = فاصله P2→P3 به درصد ATR
  - has_close = آیا بین P2 و P3، close حداقل ۱۰۰٪ ATR از P2 فاصله گرفته؟
"""

def classify_pivots(pivots, candles, atr_values, max_scan=10):
    """
    پارامترها:
        pivots: لیست پیوت‌ها از calculate_zigzag (newest-first)
        candles: لیست کندل‌ها (newest-first)
        atr_values: آرایه ATR (newest-first)
        max_scan: حداکثر تعداد triplet برای بررسی (پیش‌فرض ۱۰)

    خروجی: لیست دیکشنری‌ها با کلیدهای:
        pivot, type, l1pct, l2pct, has_close, atr
    """
    classified = []
    cnt = len(pivots)
    if cnt < 3:
        return classified

    avail = cnt - 2
    to_proc = min(avail, max_scan)

    for i in range(to_proc):
        i3 = cnt - 1 - i      # جدیدترین
        i2 = i3 - 1           # وسط
        i1 = i2 - 1           # قدیمی‌تر
        if i1 < 0:
            break

        P1 = pivots[i1]
        P2 = pivots[i2]
        P3 = pivots[i3]

        atr_p = atr_values[P2['index']]
        if atr_p <= 1e-10:
            continue

        l1pct = (abs(P2['price'] - P1['price']) / atr_p) * 100.0
        l2pct = (abs(P3['price'] - P2['price']) / atr_p) * 100.0

        # has_close: بین P2 و P3، آیا close حداقل ۱۰۰٪ ATR از P2 فاصله گرفته؟
        has_close = False
        for bar in range(P2['index'], P3['index'] - 1, -1):
            if bar < 0:
                break
            pct = (abs(candles[bar]['close'] - P2['price']) / atr_p) * 100.0
            if pct >= 100.0:
                has_close = True
                break

        # بازه‌ها (دقیقاً مطابق MQL5)
        m1 = 240.0 <= l1pct < 400.0
        t1 = l1pct >= 400.0
        c2 = 100.0 <= l2pct < 240.0
        m2 = 240.0 <= l2pct < 400.0
        t2 = l2pct >= 400.0

        ptype = None
        if m1 and c2 and has_close:
            ptype = 'Std'
        elif m1 and m2:
            ptype = 'Rev'
        elif m1 and t2:
            ptype = 'Trnd'
        elif t1 and c2 and has_close:
            ptype = 'Liq'
        else:
            continue

        classified.append({
            'pivot': P2,
            'type': ptype,
            'l1pct': l1pct,
            'l2pct': l2pct,
            'has_close': has_close,
            'atr': atr_p,
        })

    return classified