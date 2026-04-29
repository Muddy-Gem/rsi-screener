from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import ta
import threading
import time
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# 캐시 (전역 상태)
cache = {
    'data': [],
    'all_data': [],
    'timestamp': None,
    'status': 'idle',  # idle, scanning, done, error
    'progress': 0,
    'total': 0,
    'error': None
}

def get_sample_stocks():
    stocks = [
        {'name': '삼성전자', 'code': '005930', 'market': 'KOSPI'},
        {'name': 'SK하이닉스', 'code': '000660', 'market': 'KOSPI'},
        {'name': 'LG에너지솔루션', 'code': '373220', 'market': 'KOSPI'},
        {'name': '삼성바이오로직스', 'code': '207940', 'market': 'KOSPI'},
        {'name': '현대차', 'code': '005380', 'market': 'KOSPI'},
        {'name': '기아', 'code': '000270', 'market': 'KOSPI'},
        {'name': 'POSCO홀딩스', 'code': '005490', 'market': 'KOSPI'},
        {'name': 'LG화학', 'code': '051910', 'market': 'KOSPI'},
        {'name': '삼성SDI', 'code': '006400', 'market': 'KOSPI'},
        {'name': 'KB금융', 'code': '105560', 'market': 'KOSPI'},
        {'name': '신한지주', 'code': '055550', 'market': 'KOSPI'},
        {'name': '하나금융지주', 'code': '086790', 'market': 'KOSPI'},
        {'name': '카카오', 'code': '035720', 'market': 'KOSPI'},
        {'name': 'NAVER', 'code': '035420', 'market': 'KOSPI'},
        {'name': '셀트리온', 'code': '068270', 'market': 'KOSPI'},
        {'name': '한화오션', 'code': '042660', 'market': 'KOSPI'},
        {'name': 'HD현대중공업', 'code': '329180', 'market': 'KOSPI'},
        {'name': '두산에너빌리티', 'code': '034020', 'market': 'KOSPI'},
        {'name': 'LG전자', 'code': '066570', 'market': 'KOSPI'},
        {'name': '삼성물산', 'code': '028260', 'market': 'KOSPI'},
        {'name': '현대모비스', 'code': '012330', 'market': 'KOSPI'},
        {'name': 'SK이노베이션', 'code': '096770', 'market': 'KOSPI'},
        {'name': 'KT&G', 'code': '033780', 'market': 'KOSPI'},
        {'name': '한국전력', 'code': '015760', 'market': 'KOSPI'},
        {'name': '롯데케미칼', 'code': '011170', 'market': 'KOSPI'},
        {'name': 'HLB', 'code': '028300', 'market': 'KOSDAQ'},
        {'name': '에코프로비엠', 'code': '247540', 'market': 'KOSDAQ'},
        {'name': '에코프로', 'code': '086520', 'market': 'KOSDAQ'},
        {'name': '셀바스AI', 'code': '108860', 'market': 'KOSDAQ'},
        {'name': '제룡전기', 'code': '033100', 'market': 'KOSDAQ'},
        {'name': '알테오젠', 'code': '196170', 'market': 'KOSDAQ'},
        {'name': '리가켐바이오', 'code': '141080', 'market': 'KOSDAQ'},
        {'name': '클래시스', 'code': '214150', 'market': 'KOSDAQ'},
        {'name': '레인보우로보틱스', 'code': '277810', 'market': 'KOSDAQ'},
        {'name': '삼천당제약', 'code': '000250', 'market': 'KOSDAQ'},
        {'name': '파마리서치', 'code': '214450', 'market': 'KOSDAQ'},
        {'name': '오스템임플란트', 'code': '048260', 'market': 'KOSDAQ'},
        {'name': '펄어비스', 'code': '263750', 'market': 'KOSDAQ'},
        {'name': 'HPSP', 'code': '403870', 'market': 'KOSDAQ'},
        {'name': '솔브레인', 'code': '357780', 'market': 'KOSDAQ'},
    ]
    return pd.DataFrame(stocks)

def calculate_rsi(code, period=14):
    try:
        # KS 시도
        stock = yf.Ticker(f"{code}.KS")
        hist = stock.history(period="3mo")

        if hist.empty:
            stock = yf.Ticker(f"{code}.KQ")
            hist = stock.history(period="3mo")

        if hist.empty or len(hist) < period + 1:
            return None, None, None

        rsi_series = ta.momentum.RSIIndicator(hist['Close'], window=period).rsi()
        current_rsi = round(float(rsi_series.iloc[-1]), 2)
        current_price = round(float(hist['Close'].iloc[-1]), 0)
        prev_price = round(float(hist['Close'].iloc[-2]), 0)
        change_pct = round((current_price - prev_price) / prev_price * 100, 2)

        return current_rsi, current_price, change_pct
    except Exception as e:
        return None, None, None

def run_scan(stocks_df):
    """백그라운드 스레드에서 스캔 실행"""
    cache['status'] = 'scanning'
    cache['data'] = []
    cache['all_data'] = []
    cache['progress'] = 0
    cache['total'] = len(stocks_df)
    cache['error'] = None

    results = []

    for i, row in stocks_df.iterrows():
        if cache['status'] == 'idle':  # 중단 요청 시
            break

        cache['progress'] = i + 1
        code = str(row['code']).zfill(6)
        name = row['name']
        market = row['market']

        rsi, price, change_pct = calculate_rsi(code)

        if rsi is not None:
            entry = {
                'name': name,
                'code': code,
                'market': market,
                'rsi': rsi,
                'price': price,
                'change_pct': change_pct,
                'signal': '강한 매수' if rsi <= 30 else ('매수 고려' if rsi <= 40 else '관망')
            }
            results.append(entry)

        time.sleep(0.05)

    results.sort(key=lambda x: x['rsi'])
    cache['all_data'] = results
    cache['data'] = [r for r in results if r['rsi'] <= 40]
    cache['status'] = 'done'
    cache['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cache['progress'] = cache['total']

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

@app.route('/api/quick-scan', methods=['GET', 'POST'])
def quick_scan():
    if cache['status'] == 'scanning':
        return jsonify({'message': '이미 스캔 중입니다.', 'status': 'scanning'})

    stocks_df = get_sample_stocks()
    # 백그라운드 스레드로 실행
    t = threading.Thread(target=run_scan, args=(stocks_df,))
    t.daemon = True
    t.start()

    return jsonify({'message': '스캔 시작됨', 'status': 'scanning', 'total': len(stocks_df)})

@app.route('/api/scan', methods=['GET', 'POST'])
def full_scan():
    if cache['status'] == 'scanning':
        return jsonify({'message': '이미 스캔 중입니다.', 'status': 'scanning'})

    stocks_df = get_sample_stocks()  # 전체 스캔도 동일 (추후 확장 가능)
    t = threading.Thread(target=run_scan, args=(stocks_df,))
    t.daemon = True
    t.start()

    return jsonify({'message': '전체 스캔 시작됨', 'status': 'scanning', 'total': len(stocks_df)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
