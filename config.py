db = {
    # 데이터베이스에 접속할 사용자 아이디
    'user': 'root',
    # 사용자 비밀번호
    'password': 'xodus123',
    # 접속할 데이터베이스의 주소 (같은 컴퓨터에 있는 데이터베이스(로컬)에 접속할 땐 '127.0.0.1')
    'host': '127.0.0.1',
    # 관계형 데이터베이스는 주로 3306 포트를 통해 연결됨
    'port': 3306,
    # 실제 사용할 데이터베이스 이름
    'database': 'community_users'
}

# SQLAlchemy의 DB URL 작성법:
# "dialect+driver://username:password@host:port/database"
DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"