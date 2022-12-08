
from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
from sqlalchemy import create_engine, text
# mysql-connector-python
from datetime import timedelta

import math
import json

app = Flask(__name__)
app.secret_key = "111222333"
# app.config["SECRET_KEY"] = "abcd" # 예시라 간단한 값으로 지정했지만, 실제로는 이런 단순한 값 사용하면 절대 X
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=1) # 세션유지 시간을 30분으로 지정
# => 로그인(세션설정) 기능 구현할 때 이런 것도 있다.

#  튜플에서 딕셔너리로 cursor= db.cursor(pymysql.cursors.DictCursor)

# db 연결
# 참고 - https://problem-solving.tistory.com/10
# 참고 - https://shanepark.tistory.com/64


# route
# @app.route('/')
# def root_test():
#     data = text('''
#                 SELECT *
#                 FROM board;
#                 ''')
#     rows = app.database.execute(data).fetchall()
#     print(rows[:10])
#
#     # return 가능한 상태로 만들기 1: 행마다 키값을 하나하나 지정해서 딕셔너리 모음으로 만든다.
#     temp = []
#     for row in rows[:10]:
#         one = {
#             'id': row[0],
#             'title': row[1],
#             'content': row[2], 'user_id': row[3], 'category': row[4],
#                'created_at': row[5]}
#         temp.append(one)
#     print(temp)
#
#     # return 가능한 상태로 만들기 2: 이 legacyRow라는 애가
#     # return은 불가능하고 왜인지 for루프로는 돌아진다면, iterable이라는 얘긴데,
#     # 그렇다면 행마다 그냥 list()로 한 번에 바꿔버릴 수 있지 않을까? => 된다.
#     temp2 = []
#     for row in rows[:10]:
#         temp2.append(list(row))
#     print(temp2)
#
#     # return 가능한 상태로 만들기 3-1: json의 dumps 이용하기 => 전체 리스트가 하나의 문자열이 되어버림.
#     json_rows = json.dumps(rows, default=str, ensure_ascii=False) # flask.json.dumps가 맞는가...
#     print(type(json_rows[0]), json_rows[0])
#
#     # return 가능한 상태로 만들기 3-2: json의 loads로 json 형태로 되돌리기
#     # => 전체가 다시 리스트가 되어 행별로는 나눠지지만 각 인덱스(행)이 다시 문자열이다.
#     json_rows_dumped = json.loads(json_rows) # flask.json.dumps가 맞는가...
#     print(type(json_rows_dumped[0]), json_rows_dumped[0])
#     json_rows_dumped_foreach = []
#     return json_rows_dumped[:10]
#     for row in json_rows_dumped:
#         json_rows_dumped_foreach.append(json.loads(row))
#     return json_rows_dumped_foreach[:10]
#     # print(board_list[:10])
#     # return render_template('index.html', component_name='mainBoard')

# route
@app.route('/')
def root():
    return mainBoardLayout()


# get layout
@app.route('/groups-layout')
def groupsLayout():
    return render_template('index.html', component_name='groups')

# @app.route('/users-layout')
# def usersLayout():
#     return render_template('index.html', component_name='users', users_list=_get_users())

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


# -----------------------------------------------------
# 재원님 - 게시글 보기!
# @app.route('/postView-layout')
# def postView():
#     index = request.args.get("index", 1, type=int)
#     post = boardView(index)
#     return render_template('index.html', component_name='postView', post=post)

@app.route('/postView-layout')
def postView():
    index = request.args.get("index", 1, type=int)
    post = boardView(index)
    print(post)
    # title = post[1]
    # content = post[2]
    return render_template('index.html', component_name='postView', post=post)

# GET specific comment
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

    # 조회수 (먼저?) 증가시키기
    data = text('''
                    UPDATE board 
                    SET view = view + 1
                    
                    WHERE id = :index;
                    ''')
    app.database.execute(data, placeholder)
    return list(result)
    # board = list(result)
    # board = {
    #     'id': result[0],
    #     'title': result[1],
    #     'content': result[2],
    #     'user_nick': result[3],
    #     'view': result[4]
    # }
    # return jsonify(board)

#--------------------------------------

#----------------------------------------
# 기민님
# 게시글 작성 페이지
@app.route('/postWirte-layout')
def write():
    return render_template('index.html', component_name='boardWrite')

@app.route('/write', methods=['POST'])
def board_write():
    title = request.form['title']
    content = request.form['content']
    sql = text('''
                INSERT INTO board (title,content)
                VALUES (:title, :content);
                ''')
    placeholder = {'title': title, 'content': content}
    app.database.execute(sql, placeholder)

    return "success"  #등록 버튼 누른 후 보여지는 메세지 등록 버튼을 누르면 저장과 함계 게시글 목록으로 이동

# 게시글 수정 페이지
@app.route('/boardModify-layout')
def show_board_modify():
    return render_template('index.html', component_name='boardModify')

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


    else: # methods="post"일 때 작동 코드
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

        return jsonify({'msg':'수정 완료'})

#-----------------------


@app.route('/images-layout')
def imagesLayout():
    return render_template('index.html', component_name='images')

@app.route('/signup-layout')
def singupLayout():
    return render_template('index.html', component_name='signup')

@app.route('/login-layout')
def loginLayout():
    return render_template('index.html', component_name='login')

@app.route('/search-layout')
def searchLayout():
    return render_template('index.html', component_name='search')

@app.route('/search', methods=["POST", "GET"])
def search_users():
    if request.method == 'POST':
        # user_id = request.form['id']
        # user_password = request.form['password']
        # user_name = request.form['user_name'] # unique값
        last_name = request.form['last_name'] # unique 아닌 값
        data = text('''
                    SELECT *
                    FROM user AS u
                    WHERE last_name = :last_name
                    ''')
        members = app.database.execute(data, {'last_name' : last_name}).fetchall()
        count = len(members)
        return render_template('index.html', component_name='search', members=members, cnt=count)


# POST a user information : 회원 가입
@app.route('/user', methods=['POST'])
def insert_user():
    # 프론트로부터 유저 정보 받아서 user 테이블에 넣기
    new_user = request.json # flask버전 request는 json이 아니라 get_json이라던데..? 아, get_json()을 내부적으로 호출한다고 한다.
    data = text('''
                    INSERT INTO user (first_name, last_name, user_name)
                    VALUES (:first_name, :last_name, :user_name)
                    ''')
    print(data)
    new_user_id = app.database.execute(data, new_user).lastrowid

    print("result", new_user_id)
    return "User insert success", 200


def _get_users():
    login_id = "abcd"
    data = text('''
                    SELECT *
                    FROM user AS u
                     ''')
    users = app.database.execute(data).fetchall()
    return users


# @app.route('/user', methods=['GET'])
# def get_users():
#     data = text('''
#                 SELECT *
#                 FROM user AS u
#                 ''')
#     rows = app.database.execute(data).fetchall()
#     json_rows = json.dumps(rows, default=str, ensure_ascii=False) # flask.json.dumps가 맞는가...
#     print(type(json_rows), json_rows)
#     return json_rows

# @app.route('/mypage/modify', methods=["POST"])
# def modify():
#     # data = request.get_json()
#     # print(data)
#     # pwd = request.get_json().get('pwd')
#     # nick = request.get_json().get('nick')
#     # login_id = request.get_json().get('login_id')
#     pwd = request.form['pwd']
#     nick = request.form['nick']
#     login_id = request.form['login_id']
#
#     sql = f'update user set login_pwd = "{pwd}", user_nick = "{nick}" where login_id like "{login_id}"'
#     app.database.execute(sql)
#
#     sql = f'select * from user where login_id like "{login_id}"'
#     user_details = app.database.execute(sql).fetchone()
#     return jsonify(list(user_details))
#     return jsonify({'success':'update complete!', 'fail': 'something went wrong'})


# login 페이지 접속(GET) 처리와, "action=/login" 처리(POST)처리 모두 정의
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html', component_name='login')
    else:
        login_id = request.form['login_id']
        password = request.form['login_pwd']
        placeholder = {'login_id': login_id, 'password': password }
        try:
            sql = text('''
                        SELECT * 
                        FROM user 
                        WHERE login_id = :login_id AND login_pwd = :password;
                        ''')
            data = app.database.execute(sql, placeholder).fetchone()
            # data = User.query.filter_by(userid=userid, password=password).first()	# ID/PW 조회Query 실행
            if data is not None:	# 쿼리 데이터가 존재하면
                session['login_id'] = login_id	# userid를 session에 저장한다.
                # session.permanent = True
                # print(session)
                flash(f"로그인 성공! 아이디 {session['login_id']}")
                return redirect('/')
            else:
                flash("회원 정보가 없습니다!")
                return redirect(url_for('login'))	# 쿼리 데이터가 없으면 출력
        except:
            return "다른 이유로 로그인 실패..."	# 예외 상황 발생 시 출력

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('login_id', None)
    flash("안녕히 가세요")
    return redirect(url_for('login'))

# @app.route('/write', methods=['POST'])
# def board_write():
#     title = request.form['title']
#     content = request.form['content']
#     sql = text('''
#                 INSERT INTO board (title, content)
#                 VALUES (:title, :content);
#                 ''')
#     placeholder = {'title': title, 'content': content}
#     app.database.execute(sql, placeholder)
#     return "success"

# @app.route('/board_modify', methods=['GET', 'POST'])
# def board_modify():
#     board_id = request.args.get('id')
#     if request.method == 'GET':
#         sql = text('''
#                     SELECT *
#                     FROM board
#                     WHERE id = :board_id;
#                     ''')
#         placeholder = {'board_id': board_id}
#         board_post = list(app.database.execute(sql, placeholder).fetchone())
#         title = board_post[1]
#         content = board_post[2]
#         return render_template('boardModify.html', title=title, content=content, board_id=board_id)
#     else: # methods="post"
#         title = request.form['title']
#         content = request.form['content']
#         board_id = request.form['board_id']
#         sql = text('''
#                     UPDATE board
#                     SET title = :title, content = :content
#                     WHERE id = :board_id;
#                     ''')
#         placeholder = {'title': title, 'content': content, 'board_id': board_id}
#         app.database.execute(sql, placeholder)
#         return redirect('url')

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


#-------------------------
# 태연님
@app.route('/mypage')
def mypage():
  return render_template('mypage.html')

# 회원 정보 불러오기
@app.route('/mypage/userinfo', methods=["GET"])
def show_mypage():
    sql = "SELECT login_id, login_pwd, email, user_name, user_nick FROM user"

    rows = app.database.execute(sql)
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

    return jsonify({'msg': '탈퇴 완료'})


# @app.route('/list')
# def posts_list():



# photo

# group
# @app.route('/group')
# def getGroup():


# # 서버실행
# if __name__ == '__main__':
#     app.run(host='127.0.0.1', port=8000)


# 서버 실행
if __name__ == '__main__':
    app.config.from_pyfile('config.py')
    database = create_engine(app.config['DB_URL'], encoding='utf-8')
    app.database = database
    app.run()






