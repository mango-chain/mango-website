from flask import Flask, render_template, request, jsonify
import requests
import csv
import io
import ccxt

app = Flask(__name__)

# 구글 시트 정보 (멤버십 명부)
SHEET_ID = '1UpncS47X9zbM0FUNwOvr7jCIOsfkUugdmxgkDy1Ntlw'
GID = '830244407' # members 시트 GID

# ---------------------------------------------------------
# 페이지 라우팅
# ---------------------------------------------------------

# 1. 메인 홈페이지 (홈)
@app.route('/')
def home():
    return render_template('index.html')

# 2. 상품 구성 페이지
@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

# 3. 자동매매봇 입장 페이지 (추가됨)
@app.route('/bot')
def bot():
    return render_template('bot.html')

# 4. 실시간 성과 페이지 (추가됨)
@app.route('/performance')
def performance():
    return render_template('performance.html')

# 5. 대시보드 페이지 (로그인 후 이동)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# ---------------------------------------------------------
# [API] 5대 거래소 선물 지갑 잔액 통합 조회
# ---------------------------------------------------------
@app.route('/api/balance', methods=['POST'])
def get_balance():
    try:
        user_code = request.json.get('code')
        
        # 1. 구글 시트에서 유저 정보 가져오기
        csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
        response = requests.get(csv_url)
        response.encoding = 'utf-8'
        
        csv_data = csv.reader(io.StringIO(response.text))
        rows = list(csv_data)
        
        target_user = None
        for row in rows:
            # A열(0): 인증코드
            if len(row) > 0 and row[0].strip().upper() == user_code.strip().upper():
                target_user = row
                break
        
        if not target_user:
            return jsonify({'status': 'error', 'message': 'User not found'})

        # 2. 시트 데이터 매핑
        # H열(7): 거래소 이름 (Binance, OKX, Bybit, Bitget, BingX)
        # I열(8): API Key
        # J열(9): Secret Key
        
        exchange_name = target_user[7].strip()
        api_key = target_user[8].strip()
        secret_key = target_user[9].strip()

        if not api_key or not secret_key:
            return jsonify({'status': 'error', 'message': 'API Key 미설정'})

        # 3. 거래소별 연결 설정 (여기가 핵심!)
        exchange_class = None
        exchange_options = {}

        if exchange_name == 'Binance':
            exchange_class = ccxt.binance
            exchange_options = {'defaultType': 'future'} # 바이낸스 선물

        elif exchange_name == 'OKX':
            exchange_class = ccxt.okx
            exchange_options = {'defaultType': 'swap'} # OKX 무기한 선물(Swap)

        elif exchange_name == 'Bybit':
            exchange_class = ccxt.bybit
            exchange_options = {'defaultType': 'linear'} # 바이비트 USDT 선물

        elif exchange_name == 'Bitget':
            exchange_class = ccxt.bitget
            exchange_options = {'defaultType': 'swap'} # 비트겟 선물

        elif exchange_name == 'BingX':
            exchange_class = ccxt.bingx
            exchange_options = {'defaultType': 'swap'} # 빙엑스 선물

        else:
            return jsonify({'status': 'error', 'message': '지원하지 않는 거래소입니다.'})

        # 4. 거래소 접속 및 잔액 조회
        exchange = exchange_class({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
            'options': exchange_options
        })
        
        # 일부 거래소는 잔액 조회 전 시장 데이터를 불러와야 안전함
        # exchange.load_markets() 

        balance = exchange.fetch_balance()
        
        # USDT 잔액 안전하게 가져오기 (없으면 0)
        usdt_balance = 0
        if 'total' in balance and 'USDT' in balance['total']:
            usdt_balance = balance['total']['USDT']
        
        # 만약 total에 없으면 free(사용가능) + used(포지션증거금) 합산 시도
        elif 'USDT' in balance:
            usdt_balance = balance['USDT'].get('total', 0)

        return jsonify({'status': 'success', 'balance': usdt_balance})

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)