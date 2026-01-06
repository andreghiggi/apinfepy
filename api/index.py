from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "FastAPI rodando na Vercel"}

@app.get("/test-db")
def test_db():
    import pymysql
    try:
        conn = pymysql.connect(
            host='mysql741.umbler.com',
            user='apinfepy',
            password='k7m2y9u4',
            database='apinfepy',
            port=41890,
            connect_timeout=5
        )
        conn.close()
        return {"status": "success", "message": "Conexão com MySQL Umbler OK"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
