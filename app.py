
from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
from sqlalchemy import create_engine, text
from datetime import timedelta

import math
import json

app = Flask(__name__)
app.secret_key = "111222333"
# app.config["SECRET_KEY"] = "abcd" # 예시라 간단한 값으로 지정했지만, 실제로는 이런 단순한 값 사용하면 절대 X
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30) # 세션유지 시간을 30분으로 지정


# route
@app.route('/')
def root():
    return mainBoardLayout()


#----------------------------------------
# 희선님 - 회원가입, 로그인

# 회원가입 화면 그리기
@app.route('/signup-layout')
def singupLayout():
    return render_template('index.html', component_name='signup')

# @app.route('/signup')
# def signup():
#     return render_template('index.html', component_name='signup')

# 회원가입 처리
@app.route('/signup/userinfo', methods=["POST"])
def show_signup():
    signup_id = request.form['signup_id']
    signup_pw = request.form['signup_pw']
    signup_name = request.form['signup_name']
    signup_nickname = request.form['signup_nickname']

    sql = f'INSERT INTO user (login_id, login_pwd, user_name, user_nick) VALUES ("{signup_id}", "{signup_pw}", "{signup_name}","{signup_nickname}")'
    rows = app.database.execute(sql)
    return render_template('index.html', component_name='login')


# 로그인 화면 그리기
@app.route('/login-layout')
def loginLayout():
    return render_template('index.html', component_name='login')


# 로그인 페이지 처리 - 접속(GET) 처리와 "action=/login" 처리(POST)처리
@app.route('/login/userinfo', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form['login_id']
        password = request.form['login_pwd']
        placeholder = {'login_id': login_id, 'password': password}
        try:
            sql = text('''
                        SELECT * 
                        FROM user 
                        WHERE login_id = :login_id AND login_pwd = :password;
                        ''')
            user = app.database.execute(sql, placeholder).fetchone()
            print(user, user[4])
            # data = User.query.filter_by(userid=userid, password=password).first()	# ID/PW 조회Query 실행
            if user is not None:  # 쿼리 데이터가 존재하면
                session['login_id'] = login_id  # userid를 session에 저장한다.
                session['user_nick'] = user[4]  # user의 닉네임을 session에 저장한다.
                session['user_id'] = user[0]  # user의 교유번호 (id)를 session에 저장한다.
                # session.permanent = True
                # print(session)
                flash(f"{user[4]}님 반갑습니다!")  # 로그인 시 이 메세지가 뜨지 않고 ajax의 success 부분이 실행된다. 
                return redirect('/')
            else:
                flash("회원 정보가 없습니다!")
                return redirect(url_for('login'))  # 쿼리 데이터가 없으면 출력
        except:
            return "다른 이유로 로그인 실패..."  # 예외 상황 발생 시 출력
    else:
        return render_template('index.html', component_name='login')


# 로그아웃 처리
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('mainBoardLayout'))


#-------------------------------
# 태연님 - 마이페이지 보기 & 수정, 회원정보 삭제
@app.route('/mypage')
def mypage():
  return render_template('mypage.html')

# 회원 정보 불러오기
@app.route('/mypage/userinfo', methods=["GET"])
def show_mypage():
    sql = text('''
            SELECT login_id, login_pwd, email, user_name, user_nick 
            FROM user 
            where login_id like :login_id;
            ''')
    placeholder = {'login_id': session['login_id']}

    rows = app.database.execute(sql, placeholder)
    list = []
    for info in rows:
        temp = {
            'id': info[0],
            'pwd': info[1],
            'email': info[2],
            'name': info[3],
            'nick': info[4]
        }
        list.append(temp)
    print(list)

    return jsonify({'msg': list})


# 회원 정보 수정하기
@app.route('/mypage/modify', methods=["POST"])
def modify():
    # print(request.get_json())
    # pwd = request.get_json().get('pwd')
    # nick = request.get_json().get('nick')
    # user_id = request.get_json().get('login_id')
    print(request.form)
    pwd = request.form['pwd']
    nick = request.form['nick']
    login_id = request.form['login_id']

    sql = f'update user set login_pwd = "{pwd}", user_nick = "{nick}" where login_id like "{login_id}"'
    app.database.execute(sql)

    userDetails = app.database.execute(f'select * from user where login_id like "{login_id}"').fetchone()

    return jsonify(list(userDetails))


# 회원 정보 삭제
@app.route('/mypage/delete/<login_id>', methods=["DELETE"])
def delete(login_id):
    # print(request.form)
    # login_id = request.form['login_id']
    # pwd = request.form['pwd']
    # email = request.form['email']
    # name = request.form['name']
    # nick = request.form['nick']

    sql = f'delete from user where login_id like "{login_id}"'
    app.database.execute(sql)
    # logout()
    session.clear()
    # redirect('/')
    return jsonify({'msg': '탈퇴 완료'})


# -----------------------------------------------------
# 재원님 - 게시글 보기

# 게시글 화면 그리기
@app.route('/postView-layout')
def postView():
    index = request.args.get("index", 1, type=int)
    post = boardView(index)
    return render_template('index.html', component_name='postView', post=post)


# 게시글 불러오기 처리
@app.route('/api/board/<id>', methods=["GET"])
def boardView(id):
    # 해당 id를 가진 게시글 불러오기
    data = text('''
                    SELECT b.id, title, content, u.user_nick, view
                    FROM board as b 
                    LEFT JOIN user as u 
                    ON b.user_id = u.id 
                    WHERE b.id = :index;
                    ''')
    placeholder = {'index': id}
    result = app.database.execute(data, placeholder).fetchone()

    # 조회수 증가시키기
    data = text('''
                    UPDATE board 
                    SET view = view + 1
                    
                    WHERE id = :index;
                    ''')
    app.database.execute(data, placeholder)
    return list(result)


#----------------------------------------
# 기민님 - 게시글 작성 & 수정

# 게시글 작성 페이지 그리기
@app.route('/postWirte-layout')
def write():
    return render_template('index.html', component_name='boardWrite')


# 게시글 작성 페이지 처리
@app.route('/write', methods=['POST'])
def board_write():
    title = request.form['title']
    content = request.form['content']
    category_name = 'G'

    sql = text('''
                INSERT INTO board (title,content, category_name, user_id)
                VALUES (:title, :content, :category_name, :user_id);
                ''')
    placeholder = {'title': title, 'content': content, 'category_name': category_name, 'user_id': session['user_id']}
    app.database.execute(sql, placeholder)
    return redirect(url_for('categoryBoardLayout'))  #등록 버튼 누른 후 보여지는 메세지 등록 버튼을 누르면 저장과 함계 게시글 목록으로 이동


# 게시글 수정 페이지 그리기
@app.route('/boardModify-layout')
def show_board_modify():
    return render_template('index.html', component_name='boardModify')


# 게시글 수정 페이지 처리
@app.route('/board_modify', methods=['GET', 'POST'])
def board_modify():
    # board_id = 1  #####
    board_id = request.args.get('board_id', 1, type=int)
    if request.method == 'GET':
        sql = text('''
                    SELECT *
                    FROM board
                    WHERE id = :board_id;
                    ''')
        placeholder = {'board_id': board_id}
        print(board_id)
        print(sql)
        # app.database.execute(sql, placeholder)
        board_post = list(app.database.execute(sql, placeholder).fetchone())
        title = board_post[1]
        content = board_post[2]
        print(title, content)
        return render_template('index.html', component_name='boardModify', title=title, content=content, board_id=board_id)

    else: # method =="post"일 때 작동 코드
        title = request.form['title']
        content = request.form['content']
        board_id = request.form['board_id']
        sql = text('''
                    UPDATE board
                    SET title = :title, content = :content
                    where id = :board_id;
                    ''')
        placeholder = {'title': title, 'content': content, 'board_id': board_id}
        app.database.execute(sql, placeholder)
        return jsonify({'msg': '수정 완료'})


#--------------------------------------
#--------------------------------------
# 희서님

# 메인 게시판 그리기
@app.route('/mainBoard-layout')
def mainBoardLayout():
    category1 = _get_mainBoard_posts(1)
    category2 = _get_mainBoard_posts(2)
    category3 = _get_mainBoard_posts(3)
    category4 = _get_mainBoard_posts(4)
    return render_template('index.html', component_name='mainBoard',
                           category1_list=category1,
                           category2_list=category2,
                           category3_list=category3,
                           category4_list=category4)


# 카테고리 게시판 그리기
@app.route('/categoryBoard-layout')
def categoryBoardLayout():
    category_num, post_list, page, limit, last_page_num, chunk_start, chunk_end = _get_posts(request)
    return render_template('index.html', component_name='category'+str(category_num),
                           post_list=post_list,
                           page=page,
                           limit=limit,
                           last_page_num=last_page_num,
                           chunk_start=chunk_start,
                           chunk_end=chunk_end)


# 카테고리 게시판 - 게시글 목록 불러오기 & 페이지네이션 처리
def _get_posts(request): # posts 테이블로 바꿀 것. users의 닉네임을 Join해서 가져와야 한다. # join문도 잘 가져오는 것 확인함.
    category = request.args.get("category", 1, type=int) # 1, 2, 3 혹은 4를 받을 것을 예상한다.
    data = text('''
                    SELECT b.id, title, u.user_nick, DATE_FORMAT(b.created_at, '%Y-%m-%d'), view
                    FROM board as b
                    LEFT JOIN board_category AS c
                    ON b.category_name = c.category_name
                    LEFT JOIN user AS u
                    ON b.user_id = u.id
                    WHERE c.id = :category;
                    ''')
    posts = app.database.execute(data, {'category': category}).fetchall()[::-1]

    page = request.args.get("page", 1, type=int)
    limit = 20 # 한 페이지당 출력 개수
    total_post = len(posts)
    start_post_index = (page - 1) * limit # 2페이지라면, 11~20번 게시글이 보여야함 => 인덱스로는 10~19번.
    current_page_posts = posts[start_post_index:start_post_index + limit]
    last_page_num = math.ceil(total_post / limit) # 예를 들어 93개 게시물이면 10페이지, 딱 100개의 게시물이어도 10페이지여야하므로 그냥 +1은 안된다.

    page_chunk_size = 5 # <1 2 3 4 5> 다음 표시할 페이지 뭉텅이 <6 7 8 9 10> ....
    chunk_num = int((page - 1) / page_chunk_size)
    chunk_start = (page_chunk_size * chunk_num) + 1 # 첫 뭉텅이라면 chunk_start = 1, 두 번째 뭉텅이라면 chunk_start = 6...
    chunk_end = chunk_start + (page_chunk_size -1)

    return category, current_page_posts, page, limit, last_page_num, chunk_start, chunk_end


# 메인 게시판 - 게시글 목록 불러오기 & 페이지네이션 처리
def _get_mainBoard_posts(category):
    data = text('''
                    SELECT b.id, title, u.user_nick, DATE_FORMAT(b.created_at, '%Y-%m-%d'), view
                    FROM board as b
                    LEFT JOIN board_category AS c
                    ON b.category_name = c.category_name
                    LEFT JOIN user AS u
                    ON b.user_id = u.id
                    WHERE c.id = :category
                    ORDER BY b.id DESC;
                    ''')
    placeholder = {'category': category}
    result = app.database.execute(data, placeholder).fetchmany(5)
    return result



# 서버 실행
if __name__ == '__main__':
    app.config.from_pyfile('config.py')
    database = create_engine(app.config['DB_URL'], encoding='utf-8')
    app.database = database
    app.run()






