# 1. Imagem Base: Python 3.11 leve (Slim)
FROM python:3.11-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /app

# 3. Variáveis de ambiente para otimizar o Python
# PYTHONDONTWRITEBYTECODE: Não gera arquivos .pyc (inúteis em container)
# PYTHONUNBUFFERED: Garante que os logs apareçam no terminal instantaneamente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 4. Instala dependências do SISTEMA (Linux)
# Necessário para o psycopg2 (Postgres) e bibliotecas gráficas
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copia e instala as dependências do PYTHON
# Copiamos apenas o requirements.txt primeiro para aproveitar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia todo o restante do código para dentro da pasta /app
COPY . .

# 7. Expõe a porta 5000 (Padrão do Flask)
EXPOSE 5000

# Dar permissão de execução ao script de entrada
RUN chmod +x ./docker-entrypoint.sh

# Definir o script como o ponto de entrada
ENTRYPOINT ["./docker-entrypoint.sh"]

# 8. Comando para iniciar o sistema
CMD ["uwsgi", "--ini", "uwsgi.ini"]