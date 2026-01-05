# API de Emissão de Notas Fiscais (NFe/NFCe)

Esta é uma API robusta desenvolvida em **Python** com **FastAPI** para gerenciar e emitir Notas Fiscais Eletrônicas. Ela foi projetada para ser integrada facilmente a sistemas SaaS.

## 🚀 Tecnologias Utilizadas

- **FastAPI**: Framework web de alta performance.
- **SQLAlchemy**: ORM para persistência de dados.
- **SQLAdmin**: Interface web de administração automática.
- **PyNFe**: Biblioteca para comunicação com os webservices da SEFAZ.
- **SQLite**: Banco de dados inicial (pode ser trocado por PostgreSQL/MySQL facilmente).

## 🛠️ Como Executar

1. **Instale as dependências**:
   ```bash
   pip install fastapi uvicorn sqlalchemy sqladmin pynfe pydantic python-multipart
   ```

2. **Inicie a API**:
   ```bash
   python main.py
   ```

3. **Acesse as interfaces**:
   - **Documentação Interativa (Swagger)**: `http://localhost:8000/docs`
   - **Painel de Administração**: `http://localhost:8000/admin`
   - **API Root**: `http://localhost:8000`

## 📂 Estrutura do Projeto

- `main.py`: Ponto de entrada e configuração do servidor/admin.
- `models.py`: Definição das tabelas do banco de dados (Empresas, Notas).
- `routes.py`: Endpoints da API para integração com seu App.
- `schemas.py`: Validação de dados (Pydantic).
- `fiscal_service.py`: Lógica de integração com a SEFAZ via PyNFe.

## 📝 Fluxo de Integração

1. **Cadastre sua Empresa**: Via Admin ou endpoint `POST /api/v1/empresas`.
2. **Envie os dados da Nota**: Use o endpoint `POST /api/v1/notas-fiscais`.
3. **Emita a Nota**: Chame o endpoint `POST /api/v1/notas-fiscais/{id}/emitir`.

## ⚠️ Observações Importantes

- **Certificado Digital**: Para emissão real, você precisará carregar seu certificado `.pfx` e configurar a senha no cadastro da empresa.
- **Ambiente**: O sistema suporta Homologação (testes) e Produção.
- **Gratuidade**: O uso desta API é totalmente gratuito, você paga apenas pela sua infraestrutura (VPS).
