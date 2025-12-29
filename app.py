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

# 3. 자동매매봇 입장 페이지 (추가됨)
@app.route('/bot')
def bot():
    return render_template('bot.html')

# 4. 실시간 성과 페이지 (추가됨)
@app.route('/performance')
def performance():
    return render_template('performance.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)