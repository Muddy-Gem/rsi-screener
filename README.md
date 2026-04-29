# RSI 스크리너 - 한국 주식

## 설치 및 실행

### 1. 필수 패키지 설치
```bash
pip install flask flask-cors yfinance pandas pandas-ta requests beautifulsoup4
```

### 2. 실행
```bash
python app.py
```

### 3. 브라우저에서 접속
```
http://localhost:5000
```

---

## 기능

- **빠른 스캔**: 주요 종목 35개 RSI 분석 (30초~1분)
- **전체 스캔**: 코스피/코스닥 전 종목 (10~30분)
- **RSI 기준값 조정**: 기본 40, 자유롭게 변경 가능
- **시장 필터**: KOSPI / KOSDAQ / 전체
- **신호 구분**:
  - 🔴 RSI ≤ 30: 강한 매수 신호
  - 🟡 RSI 30~40: 매수 고려
  - ⚪ RSI > 40: 관망

---

## 데이터 소스 변경 방법

### Yahoo Finance → 한국투자증권 API로 교체 시
`app.py`의 `calculate_rsi()` 함수만 수정하면 됩니다:

```python
def calculate_rsi(code, period=14):
    # 여기만 교체하면 됩니다
    # KIS API, FinanceDataReader 등으로 변경 가능
    ...
```

---

## 주의사항
- Yahoo Finance 데이터는 **전일 종가** 기준입니다
- 실시간 데이터가 필요하면 KIS API 사용 권장
- 투자 판단은 본인 책임입니다
