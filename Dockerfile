# Imagem leve do Python (não precisamos mais do Playwright/Chromium)
FROM python:3.10-slim

# Configura o diretório de trabalho
WORKDIR /app

# Copia e instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto para o container
COPY . .

# Expõe a porta do Uvicorn
EXPOSE 8000

# Comando que roda as migrações do banco e sobe o servidor FastAPI
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
