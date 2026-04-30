from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import ta
import threading
import time
import json
import os
import concurrent.futures
from datetime import datetime
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
    'error': None
}

scan_lock = threading.Lock()

def get_stocks():
    return pd.DataFrame(STOCKS)

def fetch_stock_data(code, period=14):
    """종목 데이터 + RSI + 이동평균 + 볼린저밴드 + 52주 고저 계산
    [변경] 볼린저밴드 점수 제거 → 상승추세(+1점), 거래량증가(+1점), 눌림목(태그) 추가
    """
    try:
        hist = None
        for attempt in range(2):  # 실패 시 1회 재시도
            try:
                stock = yf.Ticker(f"{code}.KS")
                hist = stock.history(period="1y", timeout=10)
                if hist.empty:
                    stock = yf.Ticker(f"{code}.KQ")
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
        # RSI가 Signal선보다 5% 이상 위
        rsi_golden_5 = (
            not rsi_golden and
            rsi_signal.iloc[-1] > 0 and
            rsi_series.iloc[-1] >= rsi_signal.iloc[-1] * 1.05
        )

        # ── 이동평균선 ──
        ma20_series = close.rolling(min(20,n)).mean()
        ma60_series = close.rolling(min(60,n)).mean()
        ma20 = round(float(ma20_series.iloc[-1]), 0) if n >= 20 else price
        ma60 = round(float(ma60_series.iloc[-1]), 0) if n >= 60 else price
        above_ma20 = price >= ma20
        above_ma60 = price >= ma60 if n >= 60 else False
        near_ma20 = abs(price - ma20) / ma20 <= 0.03 if n >= 20 else False

        # ── MA60 우상향 (5일 전 MA60 대비 현재 MA60이 높으면 우상향) ──
        if n >= 65:
            ma60_5days_ago = round(float(ma60_series.iloc[-6]), 0)
            ma60_rising = ma60 > ma60_5days_ago
        else:
            ma60_rising = False

        # ── 상승추세: MA20 위 + MA60 우상향 ──
        is_uptrend = above_ma20 and ma60_rising

        # ── 거래량 ──
        volume = hist['Volume']
        vol_current = float(volume.iloc[-1])
        vol_ma20 = float(volume.rolling(min(20,n)).mean().iloc[-1]) if n >= 20 else vol_current
        # 거래량 이상값 필터: 0이거나 평균의 20배 초과면 신뢰 불가
        vol_valid = vol_ma20 > 0 and vol_current < vol_ma20 * 20
        vol_ratio = round(vol_current / vol_ma20, 2) if vol_ma20 > 0 else 0.0
        open_price = float(hist['Open'].iloc[-1])
        is_bullish = price > open_price  # 양봉 여부
        is_volume_surge = vol_valid and vol_ratio >= 1.2 and is_bullish

        # ── 눌림목: MA20 기준 0~10% 위 + 3일 전보다 하락 + 하락폭 -10% 이내 ──
        ma20_pct = round((price - ma20) / ma20 * 100, 2) if ma20 > 0 else 0.0
        price_3days_ago = round(float(close.iloc[-4]), 0) if n >= 4 else price
        drop_pct = (price - price_3days_ago) / price_3days_ago * 100 if price_3days_ago > 0 else 0
        is_pullback = (
            (0 <= ma20_pct <= 10) and
            (price < price_3days_ago) and
            (drop_pct >= -10)  # 급락(-10% 초과)은 눌림목 아님
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

        candle_pattern = None
        if is_hammer:     candle_pattern = '망치형'
        elif is_engulfing: candle_pattern = '장악형'
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
        if rsi_val <= 40: score += 1
        if rsi_val <= 30: score += 1      # RSI 극과매도 추가점
        if is_uptrend: score += 1         # 상승추세 (MA20 위 + MA60 우상향)
        if is_volume_surge: score += 1    # 거래량 증가 (평균 1.2배 + 양봉)
        if rsi_golden_5: score += 1       # RSI Signal선 5% 이상 위
        if is_pullback: score += 1        # 눌림목 (MA20 근처 + 3일 하락)
        if candle_pattern: score += 1     # 캔들패턴 (망치형/장악형/장대양봉)

        if score >= 5:   signal = '강력매수'
        elif score >= 3: signal = '매수유망'
        elif rsi_val <= 30: signal = '강한매수'
        elif rsi_val <= 40: signal = '매수고려'
        else:            signal = '관망'

        result = {
            'name': None, 'code': code, 'market': None,
            'price': price, 'change_pct': change,
            'rsi': rsi_val, 'rsi_golden': rsi_golden, 'rsi_golden_5': rsi_golden_5,
            'ma20': ma20, 'ma60': ma60,
            'above_ma20': above_ma20, 'above_ma60': above_ma60, 'near_ma20': near_ma20,
            'ma60_rising': ma60_rising, 'is_uptrend': is_uptrend,
            'vol_ratio': vol_ratio, 'is_bullish': is_bullish, 'is_volume_surge': is_volume_surge,
            'is_pullback': is_pullback, 'ma20_pct': ma20_pct,
            'candle_pattern': candle_pattern,
            'bb_upper': bb_upper, 'bb_lower': bb_lower, 'bb_mid': bb_mid, 'bb_pct': bb_pct,
            'near_bb_lower': near_bb_lower,
            'high_52': high_52, 'low_52': low_52,
            'pct_from_low': pct_from_low, 'pct_from_high': pct_from_high,
            'score': score, 'signal': signal,
        }
        # numpy 타입 → Python 기본 타입 변환 (JSON 직렬화 오류 방지)
        import numpy as np
        def to_python(v):
            if isinstance(v, (np.bool_)):    return bool(v)
            if isinstance(v, (np.integer)):  return int(v)
            if isinstance(v, (np.floating)): return float(v)
            return v
        return {k: to_python(v) for k, v in result.items()}
    except Exception as e:
        return None

def save_cache():
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'data': cache['data'], 'all_data': cache['all_data'], 'timestamp': cache['timestamp']}, f, ensure_ascii=False)
    except Exception as e:
        print(f"캐시 저장 오류: {e}")

def load_cache():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                cache['data'] = saved.get('data', [])
                cache['all_data'] = saved.get('all_data', [])
                cache['timestamp'] = saved.get('timestamp')
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

    results = []
    rows = list(stocks_df.iterrows())

    def fetch_one(row):
        _, r = row
        code = str(r['code']).zfill(6)
        res = fetch_stock_data(code)
        cache['progress'] += 1
        if res:
            res['name'] = r['name']
            res['market'] = r['market']
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
    try:
        scan_lock.release()
    except RuntimeError:
        pass

def auto_scan_scheduler():
    while True:
        now = datetime.now()
        if now.hour == 8 and now.minute == 0:
            print(f"[{now}] 자동 스캔 시작")
            if scan_lock.acquire(blocking=False):
                t = threading.Thread(target=run_scan, args=(get_stocks(), 'auto'))
                t.daemon = True
                t.start()
        time.sleep(60)

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
    if not scan_lock.acquire(blocking=False):
        return jsonify({'message': '다른 사용자가 스캔 중입니다. 잠시 후 결과가 표시됩니다.', 'status': 'scanning', 'total': cache['total'], 'progress': cache['progress']})
    t = threading.Thread(target=run_scan, args=(get_stocks(), request.remote_addr))
    t.daemon = True
    t.start()
    return jsonify({'message': '스캔 시작됨', 'status': 'scanning', 'total': len(STOCKS)})

@app.route('/api/scan', methods=['GET','POST'])
def full_scan():
    if not scan_lock.acquire(blocking=False):
        return jsonify({'message': '다른 사용자가 스캔 중입니다.', 'status': 'scanning', 'total': cache['total'], 'progress': cache['progress']})
    t = threading.Thread(target=run_scan, args=(get_stocks(), request.remote_addr))
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
