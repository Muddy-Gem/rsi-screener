from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import ta
import threading
import time
import json
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)

# ──────────────────────────────────────────
# 종목 리스트 (200개 주요 종목)
# 나중에 KIS API로 교체 시 get_stocks() 함수만 수정하면 됨
# ──────────────────────────────────────────
STOCKS = [
    # ── KOSPI 대형주 ──
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
    {'name':'대우건설','code':'047040','market':'KOSPI'},
    {'name':'삼성엔지니어링','code':'028050','market':'KOSPI'},
    {'name':'SK건설','code':'034300','market':'KOSPI'},
    {'name':'포스코퓨처엠','code':'003670','market':'KOSPI'},
    {'name':'에코프로머티리얼즈','code':'450080','market':'KOSPI'},
    {'name':'고려아연','code':'010130','market':'KOSPI'},
    {'name':'현대제철','code':'004020','market':'KOSPI'},
    {'name':'동국제강','code':'460850','market':'KOSPI'},
    {'name':'삼성화재','code':'000810','market':'KOSPI'},
    {'name':'DB손해보험','code':'005830','market':'KOSPI'},
    {'name':'메리츠화재','code':'000060','market':'KOSPI'},
    {'name':'한국조선해양','code':'009540','market':'KOSPI'},
    {'name':'HD현대','code':'267250','market':'KOSPI'},
    {'name':'기업은행','code':'024110','market':'KOSPI'},
    {'name':'BNK금융지주','code':'138930','market':'KOSPI'},
    {'name':'DGB금융지주','code':'139130','market':'KOSPI'},
    {'name':'JB금융지주','code':'175330','market':'KOSPI'},
    {'name':'카카오뱅크','code':'323410','market':'KOSPI'},
    {'name':'크래프톤','code':'259960','market':'KOSPI'},
    {'name':'넷마블','code':'251270','market':'KOSPI'},
    {'name':'엔씨소프트','code':'036570','market':'KOSPI'},
    {'name':'카카오게임즈','code':'293490','market':'KOSPI'},
    {'name':'현대백화점','code':'069960','market':'KOSPI'},
    {'name':'신세계','code':'004170','market':'KOSPI'},
    {'name':'CJ제일제당','code':'097950','market':'KOSPI'},
    {'name':'오리온','code':'271560','market':'KOSPI'},
    {'name':'농심','code':'004370','market':'KOSPI'},
    {'name':'하이트진로','code':'000080','market':'KOSPI'},
    {'name':'롯데칠성','code':'005300','market':'KOSPI'},
    {'name':'아모레퍼시픽','code':'090430','market':'KOSPI'},
    {'name':'LG생활건강','code':'051900','market':'KOSPI'},
    {'name':'한미약품','code':'128940','market':'KOSPI'},
    {'name':'유한양행','code':'000100','market':'KOSPI'},
    {'name':'종근당','code':'185750','market':'KOSPI'},
    {'name':'대웅제약','code':'069620','market':'KOSPI'},
    {'name':'GC녹십자','code':'006280','market':'KOSPI'},
    {'name':'일동제약','code':'249420','market':'KOSPI'},
    {'name':'동아에스티','code':'170900','market':'KOSPI'},
    {'name':'보령','code':'003850','market':'KOSPI'},
    {'name':'현대글로비스','code':'086280','market':'KOSPI'},
    {'name':'CJ대한통운','code':'000120','market':'KOSPI'},
    {'name':'한진칼','code':'180640','market':'KOSPI'},
    {'name':'대한항공','code':'003490','market':'KOSPI'},
    {'name':'아시아나항공','code':'020560','market':'KOSPI'},
    {'name':'HMM','code':'011200','market':'KOSPI'},
    {'name':'팬오션','code':'028670','market':'KOSPI'},
    {'name':'한화솔루션','code':'009830','market':'KOSPI'},
    {'name':'OCI홀딩스','code':'010060','market':'KOSPI'},
    {'name':'효성첨단소재','code':'298050','market':'KOSPI'},
    {'name':'코오롱인더','code':'120110','market':'KOSPI'},
    {'name':'SK케미칼','code':'285130','market':'KOSPI'},
    {'name':'금호석유','code':'011780','market':'KOSPI'},
    {'name':'한화','code':'000880','market':'KOSPI'},
    {'name':'두산','code':'000150','market':'KOSPI'},
    {'name':'LS','code':'006260','market':'KOSPI'},
    {'name':'세아베스틸지주','code':'001430','market':'KOSPI'},
    {'name':'현대미포조선','code':'010620','market':'KOSPI'},
    {'name':'한국항공우주','code':'047810','market':'KOSPI'},
    {'name':'LIG넥스원','code':'079550','market':'KOSPI'},
    {'name':'현대로템','code':'064350','market':'KOSPI'},
    {'name':'S-Oil','code':'010950','market':'KOSPI'},
    {'name':'GS칼텍스(GS)','code':'078930','market':'KOSPI'},
    {'name':'SK가스','code':'018670','market':'KOSPI'},
    # ── KOSDAQ 주요주 ──
    {'name':'에코프로비엠','code':'247540','market':'KOSDAQ'},
    {'name':'에코프로','code':'086520','market':'KOSDAQ'},
    {'name':'HLB','code':'028300','market':'KOSDAQ'},
    {'name':'알테오젠','code':'196170','market':'KOSDAQ'},
    {'name':'리가켐바이오','code':'141080','market':'KOSDAQ'},
    {'name':'셀바스AI','code':'108860','market':'KOSDAQ'},
    {'name':'제룡전기','code':'033100','market':'KOSDAQ'},
    {'name':'클래시스','code':'214150','market':'KOSDAQ'},
    {'name':'레인보우로보틱스','code':'277810','market':'KOSDAQ'},
    {'name':'삼천당제약','code':'000250','market':'KOSDAQ'},
    {'name':'파마리서치','code':'214450','market':'KOSDAQ'},
    {'name':'오스템임플란트','code':'048260','market':'KOSDAQ'},
    {'name':'펄어비스','code':'263750','market':'KOSDAQ'},
    {'name':'HPSP','code':'403870','market':'KOSDAQ'},
    {'name':'솔브레인','code':'357780','market':'KOSDAQ'},
    {'name':'피에스케이','code':'319660','market':'KOSDAQ'},
    {'name':'하이브','code':'352820','market':'KOSDAQ'},
    {'name':'JYP Ent','code':'035900','market':'KOSDAQ'},
    {'name':'SM','code':'041510','market':'KOSDAQ'},
    {'name':'YG엔터테인먼트','code':'122870','market':'KOSDAQ'},
    {'name':'카카오페이','code':'377300','market':'KOSDAQ'},
    {'name':'셀트리온헬스케어','code':'091990','market':'KOSDAQ'},
    {'name':'HLB생명과학','code':'067630','market':'KOSDAQ'},
    {'name':'유바이오로직스','code':'206650','market':'KOSDAQ'},
    {'name':'씨젠','code':'096530','market':'KOSDAQ'},
    {'name':'수젠텍','code':'253840','market':'KOSDAQ'},
    {'name':'엑세스바이오','code':'950130','market':'KOSDAQ'},
    {'name':'메디톡스','code':'086900','market':'KOSDAQ'},
    {'name':'휴젤','code':'145020','market':'KOSDAQ'},
    {'name':'제테마','code':'216580','market':'KOSDAQ'},
    {'name':'파이온텍','code':'196490','market':'KOSDAQ'},
    {'name':'오리엔트바이오','code':'002630','market':'KOSDAQ'},
    {'name':'녹십자셀','code':'031390','market':'KOSDAQ'},
    {'name':'차바이오텍','code':'085660','market':'KOSDAQ'},
    {'name':'바이오니아','code':'064550','market':'KOSDAQ'},
    {'name':'코미팜','code':'041960','market':'KOSDAQ'},
    {'name':'엘앤씨바이오','code':'290650','market':'KOSDAQ'},
    {'name':'티씨케이','code':'064760','market':'KOSDAQ'},
    {'name':'원익IPS','code':'240810','market':'KOSDAQ'},
    {'name':'주성엔지니어링','code':'036930','market':'KOSDAQ'},
    {'name':'테크윙','code':'089030','market':'KOSDAQ'},
    {'name':'이오테크닉스','code':'039030','market':'KOSDAQ'},
    {'name':'루닛','code':'328130','market':'KOSDAQ'},
    {'name':'뷰노','code':'338220','market':'KOSDAQ'},
    {'name':'딥노이드','code':'315640','market':'KOSDAQ'},
    {'name':'코난테크놀로지','code':'402030','market':'KOSDAQ'},
    {'name':'카카오엔터테인먼트','code':'293490','market':'KOSDAQ'},
    {'name':'위메이드','code':'112040','market':'KOSDAQ'},
    {'name':'컴투스','code':'078340','market':'KOSDAQ'},
    {'name':'NHN','code':'181710','market':'KOSDAQ'},
    {'name':'더블유게임즈','code':'192080','market':'KOSDAQ'},
    {'name':'게임빌','code':'063080','market':'KOSDAQ'},
    {'name':'데브시스터즈','code':'194480','market':'KOSDAQ'},
    {'name':'크래프톤코리아','code':'042420','market':'KOSDAQ'},
    {'name':'파수','code':'150900','market':'KOSDAQ'},
    {'name':'포스코DX','code':'022100','market':'KOSDAQ'},
    {'name':'켄코아에어로스페이스','code':'274090','market':'KOSDAQ'},
    {'name':'이수스페셜티케미컬','code':'457390','market':'KOSDAQ'},
    {'name':'엔켐','code':'348370','market':'KOSDAQ'},
    {'name':'천보','code':'278280','market':'KOSDAQ'},
    {'name':'나노신소재','code':'121600','market':'KOSDAQ'},
    {'name':'후성','code':'093370','market':'KOSDAQ'},
    {'name':'상아프론테크','code':'089980','market':'KOSDAQ'},
    {'name':'동진쎄미켐','code':'005290','market':'KOSDAQ'},
    {'name':'원익머트리얼즈','code':'104830','market':'KOSDAQ'},
    {'name':'SK바이오팜','code':'326030','market':'KOSDAQ'},
    {'name':'메지온','code':'140410','market':'KOSDAQ'},
    {'name':'올릭스','code':'226950','market':'KOSDAQ'},
    {'name':'압타바이오','code':'293780','market':'KOSDAQ'},
    {'name':'지아이이노베이션','code':'399870','market':'KOSDAQ'},
    {'name':'오가노이드사이언스','code':'419050','market':'KOSDAQ'},
    {'name':'에이비엘바이오','code':'298380','market':'KOSDAQ'},
    {'name':'보로노이','code':'310210','market':'KOSDAQ'},
    {'name':'에스티팜','code':'237690','market':'KOSDAQ'},
    {'name':'일동홀딩스','code':'000230','market':'KOSDAQ'},
    {'name':'동화약품','code':'000020','market':'KOSDAQ'},
    {'name':'제일약품','code':'271980','market':'KOSDAQ'},
    {'name':'유나이티드제약','code':'033270','market':'KOSDAQ'},
    {'name':'제이더블유홀딩스','code':'096760','market':'KOSDAQ'},
    {'name':'에스씨엠생명과학','code':'298060','market':'KOSDAQ'},
    {'name':'셀리드','code':'299660','market':'KOSDAQ'},
    {'name':'박셀바이오','code':'323990','market':'KOSDAQ'},
    {'name':'지트리비앤티','code':'115450','market':'KOSDAQ'},
    {'name':'덴티움','code':'145720','market':'KOSDAQ'},
    {'name':'인바이오','code':'302060','market':'KOSDAQ'},
    {'name':'코스메카코리아','code':'241710','market':'KOSDAQ'},
    {'name':'잉글우드랩','code':'143570','market':'KOSDAQ'},
    {'name':'실리콘투','code':'257720','market':'KOSDAQ'},
    {'name':'브이티','code':'018290','market':'KOSDAQ'},
    {'name':'한국콜마','code':'024720','market':'KOSDAQ'},
    {'name':'코스맥스','code':'192820','market':'KOSDAQ'},
    {'name':'네오팜','code':'092730','market':'KOSDAQ'},
    {'name':'제이시스메디칼','code':'287410','market':'KOSDAQ'},
    {'name':'원텍','code':'336570','market':'KOSDAQ'},
    {'name':'이루다','code':'164060','market':'KOSDAQ'},
    {'name':'피부과학','code':'347730','market':'KOSDAQ'},
    {'name':'성우하이텍','code':'015750','market':'KOSDAQ'},
    {'name':'서진시스템','code':'178320','market':'KOSDAQ'},
    {'name':'LS머트리얼즈','code':'417200','market':'KOSDAQ'},
]

# ──────────────────────────────────────────
# 캐시 파일 경로
# ──────────────────────────────────────────
CACHE_FILE = 'scan_cache.json'

# 메모리 캐시
cache = {
    'data': [], 'all_data': [], 'timestamp': None,
    'status': 'idle', 'progress': 0, 'total': 0,
    'error': None, 'scan_started_by': None
}

scan_lock = threading.Lock()

# ──────────────────────────────────────────
# 데이터 소스 함수 (KIS API로 교체 시 여기만 수정)
# ──────────────────────────────────────────
def get_stocks():
    """종목 리스트 반환. KIS API 연동 시 이 함수만 교체하면 됨."""
    return pd.DataFrame(STOCKS)

def fetch_stock_data(code, period=14):
    """
    단일 종목 RSI 계산.
    KIS API 연동 시 이 함수만 교체하면 됨.
    """
    try:
        stock = yf.Ticker(f"{code}.KS")
        hist = stock.history(period="3mo")
        if hist.empty:
            stock = yf.Ticker(f"{code}.KQ")
            hist = stock.history(period="3mo")
        if hist.empty or len(hist) < period + 1:
            return None, None, None
        rsi_s = ta.momentum.RSIIndicator(hist['Close'], window=period).rsi()
        rsi = round(float(rsi_s.iloc[-1]), 2)
        price = round(float(hist['Close'].iloc[-1]), 0)
        prev = round(float(hist['Close'].iloc[-2]), 0)
        change = round((price - prev) / prev * 100, 2)
        return rsi, price, change
    except Exception:
        return None, None, None

# ──────────────────────────────────────────
# 캐시 파일 저장/로드
# ──────────────────────────────────────────
def save_cache():
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'data': cache['data'],
                'all_data': cache['all_data'],
                'timestamp': cache['timestamp']
            }, f, ensure_ascii=False)
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
                print(f"캐시 로드: {len(cache['all_data'])}개 종목, {cache['timestamp']}")
    except Exception as e:
        print(f"캐시 로드 오류: {e}")

# ──────────────────────────────────────────
# 병렬 스캔 (20개씩 동시 처리)
# ──────────────────────────────────────────
def run_scan(stocks_df, requester_ip):
    cache['status'] = 'scanning'
    cache['data'] = []
    cache['all_data'] = []
    cache['progress'] = 0
    cache['total'] = len(stocks_df)
    cache['error'] = None
    cache['scan_started_by'] = requester_ip

    results = []
    rows = list(stocks_df.iterrows())
    BATCH = 20  # 동시 처리 수

    def fetch_one(row):
        _, r = row
        code = str(r['code']).zfill(6)
        rsi, price, change = fetch_stock_data(code)
        cache['progress'] += 1
        if rsi is not None:
            return {
                'name': r['name'], 'code': code, 'market': r['market'],
                'rsi': rsi, 'price': price, 'change_pct': change,
                'signal': '강한 매수' if rsi<=30 else ('매수 고려' if rsi<=40 else '관망')
            }
        return None

    # 배치 단위 병렬 처리
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH) as ex:
        futures = {ex.submit(fetch_one, row): row for row in rows}
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            if res:
                results.append(res)

    results.sort(key=lambda x: x['rsi'])
    cache['all_data'] = results
    cache['data'] = [r for r in results if r['rsi'] <= 40]
    cache['status'] = 'done'
    cache['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cache['progress'] = cache['total']
    cache['scan_started_by'] = None

    save_cache()

    try:
        scan_lock.release()
    except RuntimeError:
        pass

# ──────────────────────────────────────────
# 자동 스캔 스케줄러 (매일 오전 8시)
# ──────────────────────────────────────────
def auto_scan_scheduler():
    while True:
        now = datetime.now()
        # 매일 08:00 자동 스캔
        if now.hour == 8 and now.minute == 0:
            print(f"[{now}] 자동 스캔 시작")
            if scan_lock.acquire(blocking=False):
                stocks_df = get_stocks()
                t = threading.Thread(target=run_scan, args=(stocks_df, 'auto'))
                t.daemon = True
                t.start()
        time.sleep(60)  # 1분마다 체크

# ──────────────────────────────────────────
# Flask 라우트
# ──────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/status')
def get_status():
    return jsonify({
        'status': cache['status'],
        'progress': cache['progress'],
        'total': cache['total'],
        'timestamp': cache['timestamp'],
        'count': len(cache['data']),
        'error': cache['error']
    })

@app.route('/api/results')
def get_results():
    return jsonify({
        'data': cache['data'],
        'all_data': cache['all_data'],
        'timestamp': cache['timestamp'],
        'status': cache['status']
    })

@app.route('/api/quick-scan', methods=['GET','POST'])
def quick_scan():
    if not scan_lock.acquire(blocking=False):
        return jsonify({
            'message': '다른 사용자가 스캔 중입니다. 잠시 후 결과가 표시됩니다.',
            'status': 'scanning',
            'total': cache['total'],
            'progress': cache['progress']
        })
    stocks_df = get_stocks()
    t = threading.Thread(target=run_scan, args=(stocks_df, request.remote_addr))
    t.daemon = True
    t.start()
    return jsonify({'message': '스캔 시작됨', 'status': 'scanning', 'total': len(stocks_df)})

@app.route('/api/scan', methods=['GET','POST'])
def full_scan():
    if not scan_lock.acquire(blocking=False):
        return jsonify({
            'message': '다른 사용자가 스캔 중입니다. 잠시 후 결과가 표시됩니다.',
            'status': 'scanning',
            'total': cache['total'],
            'progress': cache['progress']
        })
    stocks_df = get_stocks()
    t = threading.Thread(target=run_scan, args=(stocks_df, request.remote_addr))
    t.daemon = True
    t.start()
    return jsonify({'message': '스캔 시작됨', 'status': 'scanning', 'total': len(stocks_df)})

if __name__ == '__main__':
    # 시작 시 캐시 로드
    load_cache()
    # 자동 스캔 스케줄러 시작
    scheduler = threading.Thread(target=auto_scan_scheduler)
    scheduler.daemon = True
    scheduler.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
