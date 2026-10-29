# Primeiro estágio : Build the virtual environment
FROM python:3.11-alpine AS builder

# Evitar que o python crie arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Segundo estágio: A imagem final com tamanho reduzido
FROM python:3.11-alpine

# Forcar os logs a aparecerem diretamente no console
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Criar um usuário nao root para rodar a aplicação
RUN addgroup -S appgroup && adduser -S -u 10001 -G appgroup appuser

WORKDIR /app

# Copiar somente o ambiente virtual do builder
COPY --from=builder /opt/venv /opt/venv

# Copiar o código da aplicação e aplicar a propriedade nos arquivos
COPY --chown=appuser:appgroup . .

USER appuser
EXPOSE 8002

CMD ["gunicorn", "--bind", "0.0.0.0:8002", "app:app"]
