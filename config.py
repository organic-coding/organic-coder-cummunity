from urllib.parse import quote_plus

db = {
    # 데이터베이스에 접속할 사용자 아이디
    'user': '청일점',
    # 사용자 비밀번호
    'password': quote_plus('cjddlfwja'),
    # 접속할 데이터베이스의 주소 (같은 컴퓨터에 있는 데이터베이스(로컬)에 접속할 땐 '127.0.0.1')
    'host': '192.168.0.17', # 혹시 공인으로 121.154.246.204 이거?
    # 관계형 데이터베이스는 주로 3306 포트를 통해 연결됨
    'port': 3306,
    # 실제 사용할 데이터베이스 이름
    'database': 'project_newsfeed' #'sakila'
}

# SQLAlchemy의 DB URL 작성법:
# "dialect+driver://username:password@host:port/database"
DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"

# 시도 참고(https://stackoverflow.com/questions/66876181/how-do-i-close-a-flask-sqlalchemy-connection-that-i-used-in-a-thread)
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size' : 20,
    'pool_reset_on_return' : 'commit', # looks like postgres likes this more than rollback
    'pool_timeout': 5, # try a low value here maybe
}
