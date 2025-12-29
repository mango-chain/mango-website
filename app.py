from flask import Flask, render_template

app = Flask(__name__)

# 1. 메인 홈페이지 (홈)
@app.route('/')
def home():
    return render_template('index.html')

# 2. 상품 구성 페이지
@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

# 3. 자동매매봇 페이지 (일단 로그인 화면으로 연결한다고 가정)
@app.route('/bot')
def bot():
    # 나중에 봇 대시보드를 여기에 연결할 예정입니다.
    # 지금은 임시로 "준비중" 메시지나 로그인 페이지를 띄웁니다.
    return "<h1 style='color:white; background:black; text-align:center; padding:50px;'>🤖 봇 대시보드 로그인 (준비중)</h1>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)