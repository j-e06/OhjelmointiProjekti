import mariadb
conn = mariadb.connect(
    host='127.0.0.1',
    port=3306,
    database='project',
    user='root',
    password='potatoman',
    autocommit=True
)
cursor = conn.cursor()
