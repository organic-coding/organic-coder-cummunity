from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/mypage')
def mypage():
  return render_template('mypage.html')

@app.route('/mypage/userinfo', methods=["GET"])
def show_mypage():
  
  sql = "SELECT login_id, login_pwd, email, user_name, user_nick FROM user"
  

  rows = app.database.execute(sql)
  list = []
  for info in rows:
    temp = {
      'id' : info[0],
      'pwd': info[1],
      'email': info[2],
      'name': info[3],
      'nick': info[4]
    }
    list.append(temp)
  print(list)

  return jsonify({'msg': list})
 

if __name__ == '__main__':
  app.config.from_pyfile("config.py")
  database = create_engine(app.config['DB_URL'], encoding='utf-8')
  app.database = database
  app.run(host='0.0.0.0', port=5000, debug=True)