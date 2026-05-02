from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import threading
import time
import json
import os
import tempfile
import concurrent.futures
from datetime import datetime, timedelta
import pytz

app = Flask(__name__, static_folder='static')
CORS(app)

STOCKS = [
    {'name':'삼성전자','code':'005930','market':'KOSPI'},
    {'name':'SK하이닉스','code':'000660','market':'KOSPI'},
    {'name':'LG에너지솔루션','code':'373220','market':'KOSPI'},
    {'name':'삼성바이오로직스','code':'207940','market':'KOSPI'},
    {'name':'현대차','code':'005380','market':'KOSPI'},
    {'name':'기아','code':'000270','market':'KOSPI'},
    {'name':'셀트리온','code':'068270','market':'KOSPI'},
    {'name':'POSCO홀딩스','code':'005490','market':'KOSPI'},
    {'name':'LG화학','code':'051910','market':'KOSPI'},
    {'name':'삼성SDI','code':'006400','market':'KOSPI'},
    {'name':'KB금융','code':'105560','market':'KOSPI'},
    {'name':'신한지주','code':'055550','market':'KOSPI'},
    {'name':'하나금융지주','code':'086790','market':'KOSPI'},
    {'name':'우리금융지주','code':'316140','market':'KOSPI'},
    {'name':'카카오','code':'035720','market':'KOSPI'},
    {'name':'NAVER','code':'035420','market':'KOSPI'},
    {'name':'삼성물산','code':'028260','market':'KOSPI'},
    {'name':'현대모비스','code':'012330','market':'KOSPI'},
    {'name':'LG전자','code':'066570','market':'KOSPI'},
    {'name':'SK이노베이션','code':'096770','market':'KOSPI'},
    {'name':'한화오션','code':'042660','market':'KOSPI'},
    {'name':'HD현대중공업','code':'329180','market':'KOSPI'},
    {'name':'삼성중공업','code':'010140','market':'KOSPI'},
    {'name':'한화에어로스페이스','code':'012450','market':'KOSPI'},
    {'name':'두산에너빌리티','code':'034020','market':'KOSPI'},
    {'name':'KT&G','code':'033780','market':'KOSPI'},
    {'name':'한국전력','code':'015760','market':'KOSPI'},
    {'name':'롯데케미칼','code':'011170','market':'KOSPI'},
    {'name':'SK텔레콤','code':'017670','market':'KOSPI'},
    {'name':'KT','code':'030200','market':'KOSPI'},
    {'name':'LG','code':'003550','market':'KOSPI'},
    {'name':'SK','code':'034730','market':'KOSPI'},
    {'name':'롯데쇼핑','code':'023530','market':'KOSPI'},
    {'name':'이마트','code':'139480','market':'KOSPI'},
    {'name':'현대건설','code':'000720','market':'KOSPI'},
    {'name':'GS건설','code':'006360','market':'KOSPI'},
    {'name':'포스코퓨처엠','code':'003670','market':'KOSPI'},
    {'name':'고려아연','code':'010130','market':'KOSPI'},
    {'name':'현대제철','code':'004020','market':'KOSPI'},
    {'name':'삼성화재','code':'000810','market':'KOSPI'},
    {'name':'DB손해보험','code':'005830','market':'KOSPI'},
    {'name':'메리츠화재','code':'000060','market':'KOSPI'},
    {'name':'한국조선해양','code':'009540','market':'KOSPI'},
    {'name':'HD현대','code':'267250','market':'KOSPI'},
    {'name':'기업은행','code':'024110','market':'KOSPI'},
    {'name':'BNK금융지주','code':'138930','market':'KOSPI'},
    {'name':'카카오뱅크','code':'323410','market':'KOSPI'},
    {'name':'크래프톤','code':'259960','market':'KOSPI'},
    {'name':'넷마블','code':'251270','market':'KOSPI'},
    {'name':'엔씨소프트','code':'036570','market':'KOSPI'},
    {'name':'현대백화점','code':'069960','market':'KOSPI'},
    {'name':'신세계','code':'004170','market':'KOSPI'},
    {'name':'CJ제일제당','code':'097950','market':'KOSPI'},
    {'name':'오리온','code':'271560','market':'KOSPI'},
    {'name':'농심','code':'004370','market':'KOSPI'},
    {'name':'하이트진로','code':'000080','market':'KOSPI'},
    {'name':'아모레퍼시픽','code':'090430','market':'KOSPI'},
    {'name':'LG생활건강','code':'051900','market':'KOSPI'},
    {'name':'한미약품','code':'128940','market':'KOSPI'},
    {'name':'유한양행','code':'000100','market':'KOSPI'},
    {'name':'종근당','code':'185750','market':'KOSPI'},
    {'name':'대웅제약','code':'069620','market':'KOSPI'},
    {'name':'GC녹십자','code':'006280','market':'KOSPI'},
    {'name':'현대글로비스','code':'086280','market':'KOSPI'},
    {'name':'CJ대한통운','code':'000120','market':'KOSPI'},
    {'name':'대한항공','code':'003490','market':'KOSPI'},
    {'name':'HMM','code':'011200','market':'KOSPI'},
    {'name':'한화솔루션','code':'009830','market':'KOSPI'},
    {'name':'효성첨단소재','code':'298050','market':'KOSPI'},
    {'name':'SK케미칼','code':'285130','market':'KOSPI'},
    {'name':'금호석유','code':'011780','market':'KOSPI'},
    {'name':'한화','code':'000880','market':'KOSPI'},
    {'name':'LS','code':'006260','market':'KOSPI'},
    {'name':'세아베스틸지주','code':'001430','market':'KOSPI'},
    {'name':'현대미포조선','code':'010620','market':'KOSPI'},
    {'name':'한국항공우주','code':'047810','market':'KOSPI'},
    {'name':'LIG넥스원','code':'079550','market':'KOSPI'},
    {'name':'현대로템','code':'064350','market':'KOSPI'},
    {'name':'S-Oil','code':'010950','market':'KOSPI'},
    {'name':'GS','code':'078930','market':'KOSPI'},
    {'name':'포스코인터내셔널','code':'047050','market':'KOSPI'},
    {'name':'삼성전기','code':'009150','market':'KOSPI'},
    {'name':'LG이노텍','code':'011070','market':'KOSPI'},
    {'name':'삼성에스디에스','code':'018260','market':'KOSPI'},
    {'name':'SK스퀘어','code':'402340','market':'KOSPI'},
    {'name':'카카오페이','code':'377300','market':'KOSPI'},
    {'name':'두산밥캣','code':'241560','market':'KOSPI'},
    {'name':'HD현대일렉트릭','code':'267260','market':'KOSPI'},
    {'name':'LS ELECTRIC','code':'010120','market':'KOSPI'},
    {'name':'제룡전기','code':'033100','market':'KOSDAQ'},
    {'name':'에코프로비엠','code':'247540','market':'KOSDAQ'},
    {'name':'에코프로','code':'086520','market':'KOSDAQ'},
    {'name':'HLB','code':'028300','market':'KOSDAQ'},
    {'name':'알테오젠','code':'196170','market':'KOSDAQ'},
    {'name':'리가켐바이오','code':'141080','market':'KOSDAQ'},
    {'name':'셀바스AI','code':'108860','market':'KOSDAQ'},
    {'name':'클래시스','code':'214150','market':'KOSDAQ'},
    {'name':'레인보우로보틱스','code':'277810','market':'KOSDAQ'},
    {'name':'삼천당제약','code':'000250','market':'KOSDAQ'},
    {'name':'파마리서치','code':'214450','market':'KOSDAQ'},
    {'name':'오스템임플란트','code':'048260','market':'KOSDAQ'},
    {'name':'펄어비스','code':'263750','market':'KOSDAQ'},
    {'name':'HPSP','code':'403870','market':'KOSDAQ'},
    {'name':'솔브레인','code':'357780','market':'KOSDAQ'},
    {'name':'하이브','code':'352820','market':'KOSDAQ'},
    {'name':'JYP Ent','code':'035900','market':'KOSDAQ'},
    {'name':'SM','code':'041510','market':'KOSDAQ'},
    {'name':'YG엔터테인먼트','code':'122870','market':'KOSDAQ'},
    {'name':'셀트리온헬스케어','code':'091990','market':'KOSDAQ'},
    {'name':'씨젠','code':'096530','market':'KOSDAQ'},
    {'name':'메디톡스','code':'086900','market':'KOSDAQ'},
    {'name':'휴젤','code':'145020','market':'KOSDAQ'},
    {'name':'티씨케이','code':'064760','market':'KOSDAQ'},
    {'name':'원익IPS','code':'240810','market':'KOSDAQ'},
    {'name':'주성엔지니어링','code':'036930','market':'KOSDAQ'},
    {'name':'이오테크닉스','code':'039030','market':'KOSDAQ'},
    {'name':'루닛','code':'328130','market':'KOSDAQ'},
    {'name':'뷰노','code':'338220','market':'KOSDAQ'},
    {'name':'위메이드','code':'112040','market':'KOSDAQ'},
    {'name':'컴투스','code':'078340','market':'KOSDAQ'},
    {'name':'NHN','code':'181710','market':'KOSDAQ'},
    {'name':'데브시스터즈','code':'194480','market':'KOSDAQ'},
    {'name':'포스코DX','code':'022100','market':'KOSDAQ'},
    {'name':'천보','code':'278280','market':'KOSDAQ'},
    {'name':'나노신소재','code':'121600','market':'KOSDAQ'},
    {'name':'후성','code':'093370','market':'KOSDAQ'},
    {'name':'동진쎄미켐','code':'005290','market':'KOSDAQ'},
    {'name':'원익머트리얼즈','code':'104830','market':'KOSDAQ'},
    {'name':'SK바이오팜','code':'326030','market':'KOSDAQ'},
    {'name':'에이비엘바이오','code':'298380','market':'KOSDAQ'},
    {'name':'에스티팜','code':'237690','market':'KOSDAQ'},
    {'name':'덴티움','code':'145720','market':'KOSDAQ'},
    {'name':'실리콘투','code':'257720','market':'KOSDAQ'},
    {'name':'브이티','code':'018290','market':'KOSDAQ'},
    {'name':'한국콜마','code':'024720','market':'KOSDAQ'},
    {'name':'코스맥스','code':'192820','market':'KOSDAQ'},
    {'name':'제이시스메디칼','code':'287410','market':'KOSDAQ'},
    {'name':'원텍','code':'336570','market':'KOSDAQ'},
    {'name':'서진시스템','code':'178320','market':'KOSDAQ'},
    {'name':'LS머트리얼즈','code':'417200','market':'KOSDAQ'},
    {'name':'엔켐','code':'348370','market':'KOSDAQ'},
    {'name':'피에스케이','code':'319660','market':'KOSDAQ'},
    {'name':'HLB생명과학','code':'067630','market':'KOSDAQ'},
    {'name':'올릭스','code':'226950','market':'KOSDAQ'},
    {'name':'보로노이','code':'310210','market':'KOSDAQ'},
    {'name':'코난테크놀로지','code':'402030','market':'KOSDAQ'},
    {'name':'더블유게임즈','code':'192080','market':'KOSDAQ'},
    {'name':'네오팜','code':'092730','market':'KOSDAQ'},
    {'name':'이루다','code':'164060','market':'KOSDAQ'},
    {'name':'성우하이텍','code':'015750','market':'KOSDAQ'},
]

CACHE_FILE = 'scan_cache.json'

cache = {
    'data': [], 'all_data': [], 'timestamp': None,
    'status': 'idle', 'progress': 0, 'total': 0,
    'error': None, 'kospi_market_up': None, 'kosdaq_market_up': None
}

scan_lock = threading.Lock()
progress_lock = threading.Lock()  # progress 카운터 보호용

# IP별 마지막 스캔 시각 (DoS 방지용 cooldown)
last_scan_by_ip = {}
SCAN_COOLDOWN = timedelta(minutes=5)

def can_scan(ip):
    """IP별 쿨다운 체크 (5분에 1회 제한)"""
    if ip in ('auto', '127.0.0.1'):
        return True
    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)
    last = last_scan_by_ip.get(ip)
    if last and now - last < SCAN_COOLDOWN:
        return False
    last_scan_by_ip[ip] = now
    return True

def get_stocks():
    return pd.DataFrame(STOCKS)

def check_market_trend(ticker_symbol):
    """지수 MA60 우상향 여부 확인 (t > t-5 > t-10)"""
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period='6mo', timeout=10)
        if hist.empty or len(hist) < 70:
            return True  # 데이터 없으면 중립(True)으로 처리
        close = hist['Close']
        ma60 = close.rolling(60).mean()
        ma60_now  = float(ma60.iloc[-1])
        ma60_5d   = float(ma60.iloc[-6])
        ma60_10d  = float(ma60.iloc[-11])
        return (ma60_now > ma60_5d) and (ma60_5d > ma60_10d)
    except:
        return True  # 오류 시 중립(True)으로 처리

def check_kospi_market():
    return check_market_trend('^KS11')

def check_kosdaq_market():
    return check_market_trend('^KQ11')

def fetch_stock_data(code, market='KOSPI', period=14):
    """종목 데이터 + RSI + 이동평균 + 볼린저밴드 + 52주 고저 계산
    [변경] 볼린저밴드 점수 제거 → 상승추세(+1점), 거래량증가(+1점), 눌림목(태그) 추가
    """
    try:
        hist = None
        # 코스닥이면 KQ 먼저 시도, 코스피는 KS 먼저 시도
        primary   = '.KQ' if market == 'KOSDAQ' else '.KS'
        secondary = '.KS' if market == 'KOSDAQ' else '.KQ'
        for attempt in range(2):  # 실패 시 1회 재시도
            try:
                stock = yf.Ticker(f"{code}{primary}")
                hist = stock.history(period="1y", timeout=10)
                if hist.empty:
                    stock = yf.Ticker(f"{code}{secondary}")
                    hist = stock.history(period="1y", timeout=10)
                if not hist.empty:
                    break
            except Exception:
                if attempt == 0:
                    time.sleep(1)  # 1초 후 재시도
                else:
                    return None
        # 최소 15개(RSI용)만 있으면 처리, 부족한 지표는 기본값 사용
        if hist is None or hist.empty or len(hist) < 15:
            return None

        close = hist['Close']
        n = len(close)
        price = round(float(close.iloc[-1]), 0)
        prev  = round(float(close.iloc[-2]), 0)
        change = round((price - prev) / prev * 100, 2)

        # ── RSI ──
        rsi_series = ta.momentum.RSIIndicator(close, window=14).rsi()
        rsi_val = round(float(rsi_series.iloc[-1]), 2)

        # RSI Signal선 (9일 MA) + 골든크로스
        rsi_signal = rsi_series.rolling(window=9).mean()
        rsi_golden = (
            rsi_series.iloc[-2] <= rsi_signal.iloc[-2] and
            rsi_series.iloc[-1] > rsi_signal.iloc[-1]
        )
        # RSI골든 지속: 골든크로스 발생 후 1~2일 유지 (당일 크로스 제외)
        # 현재도 RSI > Signal 유지 중이고, 1~2일 전에 크로스가 발생했던 경우
        rsi_golden_keep = False
        if not rsi_golden and n >= 12:
            for lag in (1, 2):
                crossed = (rsi_series.iloc[-1-lag-1] <= rsi_signal.iloc[-1-lag-1] and
                           rsi_series.iloc[-1-lag]   >  rsi_signal.iloc[-1-lag])
                still_above = rsi_series.iloc[-1] > rsi_signal.iloc[-1]
                if crossed and still_above:
                    rsi_golden_keep = True
                    break
        # RSI가 Signal선보다 5% 이상 위 (골든크로스 당일·직후와 중복 방지)
        rsi_golden_5 = (
            not rsi_golden and
            not rsi_golden_keep and
            rsi_signal.iloc[-1] > 0 and
            rsi_series.iloc[-1] >= rsi_signal.iloc[-1] * 1.05
        )

        # RSI 방향: 오늘 RSI > 어제 RSI (하락 중 과매도 칼날 잡기 방지)
        rsi_rising = float(rsi_series.iloc[-1]) > float(rsi_series.iloc[-2])

        # ── 이동평균선 ──
        ma20_series = close.rolling(min(20,n)).mean()
        ma60_series = close.rolling(min(60,n)).mean()
        ma20 = round(float(ma20_series.iloc[-1]), 0) if n >= 20 else price
        ma60 = round(float(ma60_series.iloc[-1]), 0) if n >= 60 else price
        above_ma20 = price >= ma20
        above_ma60 = price >= ma60 if n >= 60 else False
        near_ma20 = abs(price - ma20) / ma20 <= 0.03 if n >= 20 else False

        # ── MA60 우상향: t > t-5 > t-10 (3포인트 비교로 안정성 강화) ──
        if n >= 70:
            ma60_5d  = round(float(ma60_series.iloc[-6]), 0)
            ma60_10d = round(float(ma60_series.iloc[-11]), 0)
            ma60_trend = (ma60 > ma60_5d) and (ma60_5d > ma60_10d)
        else:
            ma60_trend = False
            ma60_5d = ma60_10d = ma60

        # ── MA60 이격도 (현재가 / MA60) ──
        ma60_ratio = round(price / ma60, 3) if ma60 > 0 else 1.0

        # ── RSI+MA60 유효성 판단 ──
        # 추세 상승 + 이격도 85% 이상 → 유효
        # 추세 상승 + 이격도 85~95% → 유효하지만 score -1 패널티
        # 추세 하락 or 이격도 85% 미만 → 무효 (하락장)
        if ma60_trend and ma60_ratio >= 0.95:
            rsi_ma60_valid = True
            ma60_penalty = False
        elif ma60_trend and ma60_ratio >= 0.85:
            rsi_ma60_valid = True
            ma60_penalty = True   # 눌림 구간 → 점수 -1
        else:
            rsi_ma60_valid = False
            ma60_penalty = False

        ma60_rising = ma60_trend  # 기존 필드 호환성 유지

        # ── 상승추세: close > MA20 > MA60 + MA60 우상향 + 이격도 상한 1.2 ──
        # close > ma20 > ma60: 정배열 확인 (역배열 상태 제거)
        # ma60_ratio <= 1.2: 과열 구간 제거 (MA60 대비 20% 이상 급등 종목)
        ma20_above_ma60 = ma20 > ma60 if n >= 60 else False
        is_uptrend = (
            above_ma20 and
            ma20_above_ma60 and
            ma60_trend and
            ma60_ratio <= 1.2
        )

        # ── 거래량 (5중 검증: 20일평균비 + 양봉 + 5일최고비 + 전일비 + 거래대금) ──
        volume = hist['Volume']
        vol_current = float(volume.iloc[-1])
        vol_prev    = float(volume.iloc[-2])
        vol_ma20    = float(volume.rolling(min(20,n)).mean().iloc[-1]) if n >= 20 else vol_current
        vol_5day_max = float(volume.iloc[-6:-1].max()) if n >= 6 else vol_current

        # 거래대금 (현재가 × 거래량) - 50억 이상만 신뢰
        trade_value = price * vol_current
        is_liquid = trade_value >= 5_000_000_000

        # 이상값 필터: 0이거나 평균의 20배 초과면 신뢰 불가
        vol_valid = vol_ma20 > 0 and vol_current < vol_ma20 * 20
        vol_ratio = round(vol_current / vol_ma20, 2) if vol_ma20 > 0 else 0.0
        open_price = float(hist['Open'].iloc[-1])
        is_bullish = price > open_price  # 양봉 여부

        is_volume_surge = (
            vol_valid and
            vol_ratio >= 1.5 and                      # 1. 20일 평균 대비 1.5배 이상
            is_bullish and                            # 2. 양봉 (가격 상승 동반)
            vol_current >= vol_5day_max * 0.8 and    # 3. 최근 5일 최고 거래량의 80% 이상
            vol_current > vol_prev * 1.2 and         # 4. 전일 대비 1.2배 이상
            is_liquid                                 # 5. 거래대금 50억 이상
        )

        # ── 눌림목: MA20 0~10% 위 + 3일 하락 + 하락폭 -10% 이내 + 거래량 감소 ──
        ma20_pct = round((price - ma20) / ma20 * 100, 2) if ma20 > 0 else 0.0
        price_3days_ago = round(float(close.iloc[-4]), 0) if n >= 4 else price
        drop_pct = (price - price_3days_ago) / price_3days_ago * 100 if price_3days_ago > 0 else 0
        # 거래량 감소: 최근 3일 평균이 20일 평균보다 낮으면 진짜 눌림목
        vol_3day_avg = float(volume.iloc[-3:].mean()) if n >= 3 else vol_current
        vol_declining = vol_3day_avg < vol_ma20 if vol_ma20 > 0 else False
        is_pullback = (
            (0 <= ma20_pct <= 10) and
            (price < price_3days_ago) and
            (drop_pct >= -10) and      # 급락(-10% 초과)은 눌림목 아님
            vol_declining and          # 거래량 감소 = 진짜 눌림목
            is_bullish                 # 당일 양봉 = 조정 마무리 신호
        )

        # ── 캔들패턴 ──
        op = float(hist['Open'].iloc[-1])
        hi = float(hist['High'].iloc[-1])
        lo = float(hist['Low'].iloc[-1])
        cl = float(hist['Close'].iloc[-1])
        op_prev = float(hist['Open'].iloc[-2])
        cl_prev = float(hist['Close'].iloc[-2])

        body = abs(cl - op)
        candle_range = hi - lo if hi != lo else 0.0001
        lower_wick = min(op, cl) - lo
        upper_wick = hi - max(op, cl)

        # 망치형: 아래꼬리 > 몸통 2배 + 위꼬리 < 몸통 0.5배 + 양봉
        is_hammer = (
            lower_wick >= body * 2 and
            upper_wick <= body * 0.5 and
            cl > op
        )
        # 장대양봉: 몸통이 전체 캔들의 70% 이상
        is_marubozu = (
            cl > op and
            body / candle_range >= 0.7
        )
        # 상승장악형: 전일 음봉 + 오늘 양봉이 전일 몸통 완전히 감쌈
        is_engulfing = (
            cl_prev < op_prev and   # 전일 음봉
            cl > op and             # 오늘 양봉
            cl > op_prev and        # 오늘 종가 > 전일 시가
            op < cl_prev            # 오늘 시가 < 전일 종가
        )

        # 망치형 제거: 아래꼬리만 길면 조건 충족 → 노이즈 많음
        # 장악형 + 장대양봉만 유지 (명확한 매수세 확인 패턴)
        candle_pattern = None
        if is_engulfing:   candle_pattern = '장악형'
        elif is_marubozu:  candle_pattern = '장대양봉'

        # ── 볼린저밴드 (20일, 2σ) ──
        if n >= 20:
            bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
            bb_upper = round(float(bb.bollinger_hband().iloc[-1]), 0)
            bb_lower = round(float(bb.bollinger_lband().iloc[-1]), 0)
            bb_mid   = round(float(bb.bollinger_mavg().iloc[-1]), 0)
            bb_pct   = round(float(bb.bollinger_pband().iloc[-1]) * 100, 1)
        else:
            bb_upper = bb_lower = bb_mid = price
            bb_pct = 50.0
        near_bb_lower = bb_pct <= 20

        # ── 52주 고저 ──
        high_52 = round(float(close.tail(252).max()), 0)
        low_52  = round(float(close.tail(252).min()), 0)
        pct_from_low  = round((price - low_52) / low_52 * 100, 1)
        pct_from_high = round((price - high_52) / high_52 * 100, 1)

        # ── 종합 신호 점수 (0~6점) ──
        score = 0
        if rsi_val <= 40 and rsi_ma60_valid and rsi_rising: score += 1
        if rsi_val <= 30 and rsi_ma60_valid and rsi_rising: score += 1
        if is_uptrend: score += 1
        if is_volume_surge: score += 1
        # RSI골든지속 / RSI골든5% 중 하나만 점수 (중복 방지)
        if (rsi_golden_keep or rsi_golden_5) and rsi_val <= 60: score += 1
        if is_pullback: score += 1
        if candle_pattern: score += 1
        if ma60_penalty: score = max(0, score - 1)  # MA60 이격 눌림 구간 패널티

        if score >= 5 and rsi_val <= 60:              signal = '강력매수'
        elif score >= 3 and rsi_val <= 60:            signal = '매수유망'
        elif rsi_val <= 30 and rsi_ma60_valid:        signal = '강한매수'   # MA60 상승 중일 때만
        elif rsi_val <= 40 and rsi_ma60_valid:        signal = '매수고려'   # MA60 상승 중일 때만
        else:                                         signal = '관망'

        result = {
            'name': None, 'code': code, 'market': None,
            'price': price, 'change_pct': change,
            'rsi': rsi_val, 'rsi_rising': rsi_rising, 'rsi_golden': rsi_golden, 'rsi_golden_keep': rsi_golden_keep, 'rsi_golden_5': rsi_golden_5,
            'ma20': ma20, 'ma60': ma60,
            'above_ma20': above_ma20, 'above_ma60': above_ma60, 'near_ma20': near_ma20,
            'ma60_rising': ma60_rising, 'ma60_trend': ma60_trend,
            'ma60_5d': ma60_5d, 'ma60_10d': ma60_10d,
            'ma60_ratio': ma60_ratio, 'ma60_penalty': ma60_penalty,
            'rsi_ma60_valid': rsi_ma60_valid, 'is_uptrend': is_uptrend,
            'vol_ratio': vol_ratio, 'is_bullish': is_bullish, 'is_volume_surge': is_volume_surge,
            'trade_value': round(trade_value / 100000000, 1),  # 억원 단위
            'is_liquid': is_liquid,
            'is_pullback': is_pullback, 'ma20_pct': ma20_pct,
            'candle_pattern': candle_pattern,
            'bb_upper': bb_upper, 'bb_lower': bb_lower, 'bb_mid': bb_mid, 'bb_pct': bb_pct,
            'near_bb_lower': near_bb_lower,
            'high_52': high_52, 'low_52': low_52,
            'pct_from_low': pct_from_low, 'pct_from_high': pct_from_high,
            'score': score, 'signal': signal, 'market_penalty': False,
        }
        # numpy 타입 → Python 기본 타입 변환 (JSON 직렬화 오류 방지)
        def to_python(v):
            if isinstance(v, (np.bool_)):    return bool(v)
            if isinstance(v, (np.integer)):  return int(v)
            if isinstance(v, (np.floating)): return float(v)
            return v
        return {k: to_python(v) for k, v in result.items()}
    except Exception as e:
        return None

def save_cache():
    tmp_path = None
    try:
        payload = {
            'data': cache['data'],
            'all_data': cache['all_data'],
            'timestamp': cache['timestamp'],
            'kospi_market_up': cache['kospi_market_up'],
            'kosdaq_market_up': cache['kosdaq_market_up'],
        }
        dir_name = os.path.dirname(os.path.abspath(CACHE_FILE)) or '.'
        with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False,
                                         suffix='.tmp', encoding='utf-8') as tmp:
            json.dump(payload, tmp, ensure_ascii=False)
            tmp_path = tmp.name
        os.replace(tmp_path, CACHE_FILE)
        tmp_path = None  # 성공 시 정리 불필요
    except Exception as e:
        print(f"캐시 저장 오류: {e}")
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

def load_cache():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                cache['data'] = saved.get('data', [])
                cache['all_data'] = saved.get('all_data', [])
                cache['timestamp'] = saved.get('timestamp')
                cache['kospi_market_up'] = saved.get('kospi_market_up', None)
                cache['kosdaq_market_up'] = saved.get('kosdaq_market_up', None)
                cache['status'] = 'done' if cache['all_data'] else 'idle'
                print(f"캐시 로드: {len(cache['all_data'])}개 종목")
    except Exception as e:
        print(f"캐시 로드 오류: {e}")

def run_scan(stocks_df, requester_ip):
    cache['status'] = 'scanning'
    cache['data'] = []
    cache['all_data'] = []
    cache['progress'] = 0
    cache['total'] = len(stocks_df)
    cache['error'] = None

    try:
        # ── 시장 상태 체크 (코스피/코스닥 별도) ──
        kospi_up  = check_kospi_market()
        kosdaq_up = check_kosdaq_market()
        cache['kospi_market_up']  = kospi_up
        cache['kosdaq_market_up'] = kosdaq_up

        results = []
        rows = list(stocks_df.iterrows())

        def fetch_one(row):
            _, r = row
            code = str(r['code']).zfill(6)
            res = fetch_stock_data(code, market=r.get('market', 'KOSPI'))
            with progress_lock:
                cache['progress'] += 1
            if res:
                res['name'] = r['name']
                res['market'] = r['market']

                # ── 시장별 필터 적용 ──
                market = r.get('market', 'KOSPI')
                market_up = kospi_up if market == 'KOSPI' else kosdaq_up
                if not market_up:
                    res['score'] = max(0, res['score'] - 1)  # 점수 -1
                    res['market_penalty'] = True              # 종목 태그용 플래그
                    # 강력매수 → 매수유망으로 등급 제한
                    if res['signal'] == '강력매수':
                        res['signal'] = '매수유망'
                else:
                    res['market_penalty'] = False
            return res

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
            futures = {ex.submit(fetch_one, row): row for row in rows}
            for fut in concurrent.futures.as_completed(futures):
                res = fut.result()
                if res:
                    results.append(res)

        results.sort(key=lambda x: x['rsi'])
        cache['all_data'] = results
        cache['data'] = [r for r in results if r['rsi'] <= 40]
        cache['status'] = 'done'
        cache['timestamp'] = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
        cache['progress'] = cache['total']

        save_cache()

    except Exception as e:
        cache['status'] = 'error'
        cache['error'] = str(e)
        print(f"스캔 오류: {e}")

    finally:
        try:
            scan_lock.release()
        except RuntimeError:
            pass

def auto_scan_scheduler():
    """매일 오전 8시 자동 스캔 — 1초 간격으로 정각을 정밀하게 감지"""
    last_triggered_date = None
    while True:
        now = datetime.now(pytz.timezone('Asia/Seoul'))
        today = now.date()
        if now.hour == 8 and now.minute == 0 and last_triggered_date != today:
            last_triggered_date = today
            print(f"[{now}] 자동 스캔 시작")
            if scan_lock.acquire(blocking=False):
                t = threading.Thread(target=run_scan, args=(get_stocks(), 'auto'))
                t.daemon = True
                t.start()
        time.sleep(1)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/status')
def get_status():
    # 캐시 만료 여부 체크 (당일 오전 8시 이후 스캔 여부)
    is_stale = False
    if cache['timestamp']:
        try:
            kst = pytz.timezone('Asia/Seoul')
            now = datetime.now(kst)
            scan_time = kst.localize(datetime.strptime(cache['timestamp'], '%Y-%m-%d %H:%M:%S'))
            # 오늘 날짜가 다르거나, 오늘 8시 이후인데 스캔이 어제면 stale
            today_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
            is_stale = scan_time < today_8am
        except:
            is_stale = False
    return jsonify({
        'status': cache['status'], 'progress': cache['progress'],
        'total': cache['total'], 'timestamp': cache['timestamp'],
        'count': len(cache['data']), 'error': cache['error'],
        'is_stale': is_stale,
        'kospi_market_up': cache['kospi_market_up'],
        'kosdaq_market_up': cache['kosdaq_market_up'],
    })

# ── 즐겨찾기 (서버 메모리 저장, 재시작 시 초기화) ──
favorites = set()

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    return jsonify({'favorites': list(favorites)})

@app.route('/api/favorites/<code>', methods=['POST'])
def add_favorite(code):
    favorites.add(code)
    return jsonify({'favorites': list(favorites)})

@app.route('/api/favorites/<code>', methods=['DELETE'])
def remove_favorite(code):
    favorites.discard(code)
    return jsonify({'favorites': list(favorites)})

@app.route('/api/results')
def get_results():
    return jsonify({
        'data': cache['data'], 'all_data': cache['all_data'],
        'timestamp': cache['timestamp'], 'status': cache['status']
    })

@app.route('/api/quick-scan', methods=['GET','POST'])
def quick_scan():
    ip = request.remote_addr
    if not can_scan(ip):
        remaining = SCAN_COOLDOWN - (datetime.now(pytz.timezone('Asia/Seoul')) - last_scan_by_ip.get(ip, datetime.min.replace(tzinfo=pytz.timezone('Asia/Seoul'))))
        mins = int(remaining.total_seconds() / 60) + 1
        return jsonify({'message': f'너무 자주 스캔하고 있습니다. {mins}분 후 다시 시도하세요.', 'status': 'cooldown'})
    if not scan_lock.acquire(blocking=False):
        return jsonify({'message': '다른 사용자가 스캔 중입니다. 잠시 후 결과가 표시됩니다.', 'status': 'scanning', 'total': cache['total'], 'progress': cache['progress']})
    t = threading.Thread(target=run_scan, args=(get_stocks(), ip))
    t.daemon = True
    t.start()
    return jsonify({'message': '스캔 시작됨', 'status': 'scanning', 'total': len(STOCKS)})

@app.route('/api/scan', methods=['GET','POST'])
def full_scan():
    ip = request.remote_addr
    if not can_scan(ip):
        remaining = SCAN_COOLDOWN - (datetime.now(pytz.timezone('Asia/Seoul')) - last_scan_by_ip.get(ip, datetime.min.replace(tzinfo=pytz.timezone('Asia/Seoul'))))
        mins = int(remaining.total_seconds() / 60) + 1
        return jsonify({'message': f'너무 자주 스캔하고 있습니다. {mins}분 후 다시 시도하세요.', 'status': 'cooldown'})
    if not scan_lock.acquire(blocking=False):
        return jsonify({'message': '다른 사용자가 스캔 중입니다.', 'status': 'scanning', 'total': cache['total'], 'progress': cache['progress']})
    t = threading.Thread(target=run_scan, args=(get_stocks(), ip))
    t.daemon = True
    t.start()
    return jsonify({'message': '스캔 시작됨', 'status': 'scanning', 'total': len(STOCKS)})

if __name__ == '__main__':
    load_cache()
    scheduler = threading.Thread(target=auto_scan_scheduler)
    scheduler.daemon = True
    scheduler.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
