import sys
import os

# Adiciona o diretório pai ao path para que possamos importar o main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# A Vercel precisa que o objeto 'app' esteja disponível no módulo
# para que ela possa rotear as requisições corretamente.
