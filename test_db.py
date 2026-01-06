import pymysql
import sys

try:
    conn = pymysql.connect(
        host='mysql741.umbler.com',
        user='apinfepy',
        password='k7m2y9u4',
        database='apinfepy',
        port=41890,
        connect_timeout=10
    )
    print("Conexão com Umbler MySQL bem-sucedida!")
    conn.close()
except Exception as e:
    print(f"Erro ao conectar no banco da Umbler: {e}")
    sys.exit(1)
