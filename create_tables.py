from main import engine
from models import Base

print("Criando tabelas no banco da Umbler...")
try:
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")
except Exception as e:
    print(f"Erro ao criar tabelas: {e}")
