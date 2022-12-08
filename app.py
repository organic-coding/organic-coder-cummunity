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

@app.route('/mypage/modify', methods=["POST"])
def modify():
  # print(request.get_json())
  # pwd = request.get_json().get('pwd')
  # nick = request.get_json().get('nick')
  # user_id = request.get_json().get('login_id') 

  pwd = request.form['pwd']
  nick = request.form['nick']
  user_id = request.form['login_id']
 
  sql = f'update user set login_pwd = "{pwd}", user_nick = "{nick}" where login_id like "{user_id}"'
  app.database.execute(sql) 
  
  userDetails = app.database.execute(f'select * from user where login_id like "{user_id}"').fetchone()

  return jsonify(list(userDetails))


   

if __name__ == '__main__':
  app.config.from_pyfile("config.py")
  database = create_engine(app.config['DB_URL'], encoding='utf-8')
  app.database = database
  app.run(host='0.0.0.0', port=5000, debug=True)