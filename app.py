from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import ta
import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)

# 코스피/코스닥 종목 리스트 가져오기
def get_krx_stocks():
    """KRX에서 상장 종목 리스트 가져오기"""
    try:
        # 코스피
        url_kospi = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=stockMkt"
        # 코스닥
        url_kosdaq = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=kosdaqMkt"
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        df_kospi = pd.read_html(url_kospi, header=0)[0]
        df_kospi['market'] = 'KOSPI'
        
        df_kosdaq = pd.read_html(url_kosdaq, header=0)[0]
        df_kosdaq['market'] = 'KOSDAQ'
        
        df = pd.concat([df_kospi, df_kosdaq], ignore_index=True)
        df['종목코드'] = df['종목코드'].astype(str).str.zfill(6)
        
        return df[['회사명', '종목코드', 'market']].rename(columns={'회사명': 'name', '종목코드': 'code'})
    except Exception as e:
        print(f"KRX 종목 로드 실패: {e}")
        # 폴백: 샘플 종목 리스트
        return get_sample_stocks()

def get_sample_stocks():
    """샘플 주요 종목 리스트 (KRX 접근 실패 시)"""
    stocks = [
        # 코스피 대형주
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
        {'name': '롯데케미칼', 'code': '011170', 'market': 'KOSPI'},
        {'name': '한국전력', 'code': '015760', 'market': 'KOSPI'},
        # 코스닥
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
    """yfinance로 RSI 계산"""
    try:
        ticker = f"{code}.KS" if True else f"{code}.KQ"
        
        # .KS 먼저 시도
        stock = yf.Ticker(f"{code}.KS")
        hist = stock.history(period="3mo")
        
        if hist.empty:
            stock = yf.Ticker(f"{code}.KQ")
            hist = stock.history(period="3mo")
        
        if hist.empty or len(hist) < period + 1:
            return None, None, None
        
        # RSI 계산
        rsi = ta.momentum.RSIIndicator(hist['Close'], window=period).rsi()
        current_rsi = round(float(rsi.iloc[-1]), 2)
        current_price = round(float(hist['Close'].iloc[-1]), 0)
        prev_price = round(float(hist['Close'].iloc[-2]), 0)
        change_pct = round((current_price - prev_price) / prev_price * 100, 2)
        
        return current_rsi, current_price, change_pct
    except Exception as e:
        return None, None, None

# 캐시
cache = {'data': [], 'timestamp': None, 'status': 'idle', 'progress': 0, 'total': 0}

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
        'count': len(cache['data'])
    })

@app.route('/api/scan')
def scan():
    """전체 스캔 시작"""
    if cache['status'] == 'scanning':
        return jsonify({'message': '이미 스캔 중입니다.', 'status': 'scanning'})
    
    cache['status'] = 'scanning'
    cache['data'] = []
    cache['progress'] = 0
    
    stocks_df = get_krx_stocks()
    cache['total'] = len(stocks_df)
    
    results = []
    
    for i, row in stocks_df.iterrows():
        cache['progress'] = i + 1
        code = row['code']
        name = row['name']
        market = row['market']
        
        rsi, price, change_pct = calculate_rsi(code)
        
        if rsi is not None and rsi <= 40:
            results.append({
                'name': name,
                'code': code,
                'market': market,
                'rsi': rsi,
                'price': price,
                'change_pct': change_pct,
                'signal': '강한 매수' if rsi <= 30 else '매수 고려'
            })
        
        time.sleep(0.1)  # API 과부하 방지
    
    results.sort(key=lambda x: x['rsi'])
    cache['data'] = results
    cache['status'] = 'done'
    cache['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({'message': '스캔 완료', 'count': len(results), 'data': results})

@app.route('/api/results')
def get_results():
    return jsonify({
        'data': cache['data'],
        'timestamp': cache['timestamp'],
        'status': cache['status']
    })

@app.route('/api/quick-scan')
def quick_scan():
    """주요 종목만 빠르게 스캔 (샘플)"""
    cache['status'] = 'scanning'
    cache['data'] = []
    
    stocks_df = get_sample_stocks()
    cache['total'] = len(stocks_df)
    results = []
    
    for i, row in stocks_df.iterrows():
        cache['progress'] = i + 1
        code = row['code']
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
    
    results.sort(key=lambda x: x['rsi'])
    cache['data'] = [r for r in results if r['rsi'] <= 40]
    cache['status'] = 'done'
    cache['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({
        'message': '스캔 완료',
        'count': len(cache['data']),
        'data': cache['data'],
        'all_data': results
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
