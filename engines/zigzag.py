"""
موتور ZigZag پیوت Z-P-S
پورت خط به خط CalculateZigZagForTimeframe از Pivot Trex.mq5

قرارداد: candles[0] = جدیدترین
"""

MAX_ATR_PERIOD_CONST = 264
MIN_BARS_FOR_ZIGZAG = 10


def calculate_zigzag(candles, atr_values, atr_multiplier=1.0):
    """
    محاسبه پیوت‌های ZigZag.
    
    پارامترها:
        candles: لیست newest-first با کلیدهای time/open/high/low/close
        atr_values: آرایه ATR متناظر
        atr_multiplier: ضریب InpAtrMultiplier
    
    خروجی: لیست پیوت‌ها. هر پیوت:
        {time, price, index, is_high, is_candidate, close_price}
    """
    n = len(candles)
    if n < MIN_BARS_FOR_ZIGZAG:
        return []

    min_bars_req = MAX_ATR_PERIOD_CONST  # = 264
    if n <= min_bars_req + 5:
        return []

    zz_points = []

    # --- فاز ۱: پیدا کردن پیوت شروع (نزدیک قدیمی‌ترین داده) ---
    lookback = MAX_ATR_PERIOD_CONST * 2  # = 528
    if lookback >= n - min_bars_req:
        lookback = n - min_bars_req - 1
    if lookback <= 0:
        lookback = 1

    scan_start = n - 1 - min_bars_req
    scan_end = scan_start - lookback
    if scan_end < 0:
        scan_end = 0

    ihp = 0.0
    ilp = 0.0
    ihb = -1
    ilb = -1
    for k in range(scan_start, scan_end - 1, -1):
        h = candles[k]['high']
        l = candles[k]['low']
        if ihb == -1 or h > ihp:
            ihp = h
            ihb = k
        if ilb == -1 or l < ilp:
            ilp = l
            ilb = k

    if ihb == -1 or ilb == -1:
        return []

    if ihb > ilb:
        # High قدیمی‌تره → پیوت شروع = High، حالا دنبال Low
        current_trend_dir = -1
        cand_price = candles[ihb]['low']
        cand_bar = ihb
        loop_start = ihb - 1
        zz_points.append({
            'time': candles[ihb]['time'],
            'price': ihp,
            'index': ihb,
            'is_high': True,
            'is_candidate': False,
            'close_price': candles[ihb]['close'],
        })
    else:
        # Low قدیمی‌تره → پیوت شروع = Low، حالا دنبال High
        current_trend_dir = 1
        cand_price = candles[ilb]['high']
        cand_bar = ilb
        loop_start = ilb - 1
        zz_points.append({
            'time': candles[ilb]['time'],
            'price': ilp,
            'index': ilb,
            'is_high': False,
            'is_candidate': False,
            'close_price': candles[ilb]['close'],
        })

    if loop_start < 0:
        loop_start = 0

    # --- فاز ۲: حرکت به جلو در زمان (به سمت جدیدترین کندل) ---
    for i in range(loop_start, -1, -1):
        atr = atr_values[i]
        if atr <= 1e-9:
            continue
        thr = atr * atr_multiplier

        if current_trend_dir == 1:  # دنبال High
            if candles[i]['high'] > cand_price:
                cand_price = candles[i]['high']
                cand_bar = i
            if candles[i]['close'] < cand_price - thr:
                zz_points.append({
                    'time': candles[cand_bar]['time'],
                    'price': cand_price,
                    'index': cand_bar,
                    'is_high': True,
                    'is_candidate': False,
                    'close_price': candles[cand_bar]['close'],
                })
                current_trend_dir = -1
                cand_price = candles[i]['low']
                cand_bar = i
        else:  # دنبال Low
            if candles[i]['low'] < cand_price:
                cand_price = candles[i]['low']
                cand_bar = i
            if candles[i]['close'] > cand_price + thr:
                zz_points.append({
                    'time': candles[cand_bar]['time'],
                    'price': cand_price,
                    'index': cand_bar,
                    'is_high': False,
                    'is_candidate': False,
                    'close_price': candles[cand_bar]['close'],
                })
                current_trend_dir = 1
                cand_price = candles[i]['high']
                cand_bar = i

    # --- فاز ۳: افزودن پیوت کاندید (آخرین پیوت تأییدنشده) ---
    if cand_bar != -1:
        allow = True
        if len(zz_points) > 0:
            last = zz_points[-1]
            if current_trend_dir == 1 and cand_price < last['price']:
                allow = False
            if current_trend_dir == -1 and cand_price > last['price']:
                allow = False
        if allow:
            zz_points.append({
                'time': candles[cand_bar]['time'],
                'price': cand_price,
                'index': cand_bar,
                'is_high': (current_trend_dir == 1),
                'is_candidate': True,
                'close_price': candles[cand_bar]['close'],
            })

    return zz_points
