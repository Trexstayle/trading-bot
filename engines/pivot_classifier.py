"""
طبقه‌بندی پیوت‌های Z-P-S به چهار نوع Std / Rev / Trnd / Liq
پورت خط به خط بخش DrawTrendLinesAndPivots از Pivot Trex.mq5
"""


def classify_pivots(zz_points, candles, atr_values, max_scan=100):
    """
    برای هر سه پیوت متوالی (P1, P2, P3) پیوت وسط (P2) را طبقه‌بندی می‌کند.
    
    پارامترها:
        zz_points: لیست پیوت‌ها از calculate_zigzag
        candles: داده کندل‌ها (newest-first)
        atr_values: آرایه ATR متناظر
        max_scan: چند پیوت آخر بررسی شود
    
    خروجی: لیست دیکشنری {pivot, type, l1pct, l2pct, has_close, atr}
    """
    classified = []
    cnt = len(zz_points)
    if cnt < 3:
        return classified

    avail = cnt - 2
    to_proc = min(avail, max_scan)

    for i in range(to_proc):
        i3 = cnt - 1 - i
        i2 = i3 - 1
        i1 = i2 - 1
        if i1 < 0:
            break

        P1 = zz_points[i1]
        P2 = zz_points[i2]
        P3 = zz_points[i3]

        atr_p = atr_values[P2['index']]
        if atr_p <= 1e-10:
            continue

        l1pct = (abs(P2['price'] - P1['price']) / atr_p) * 100.0
        l2pct = (abs(P3['price'] - P2['price']) / atr_p) * 100.0

        # has_close: در بازه P2→P3 آیا یک close حداقل ۱۰۰٪ ATR از P2 فاصله گرفته؟
        has_close = False
        for bar in range(P2['index'], P3['index'] - 1, -1):
            if bar < 0:
                break
            pct = (abs(candles[bar]['close'] - P2['price']) / atr_p) * 100.0
            if pct >= 100.0:
                has_close = True
                break

        # بازه‌ها: c=[100,240)  m=[240,400)  t=≥400
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
            'l1pct': round(l1pct, 2),
            'l2pct': round(l2pct, 2),
            'has_close': has_close,
            'atr': atr_p,
        })

    return classified
