# Primeiro estágio: Build inicial do ambiente virtual
FROM python:3.11-alpine AS builder

# Evitar a geração de arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Segundo estágio: Imagem final leve
FROM python:3.11-alpine

# Instalar o aws-cli
RUN apk update && apk add --no-cache aws-cli

# Forçar que os logs apareção na console
ENV PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Cria um usuário não root para a aplicação
RUN addgroup -S appgroup && adduser -S -u 10001 -G appgroup appuser

WORKDIR /app

# Copiar o ambiente virtual do builder
COPY --from=builder /opt/venv /opt/venv

# copia somente o app.py para executar a aplicação
COPY --chown=appuser:appgroup app.py .

USER appuser

EXPOSE 8005

CMD ["gunicorn", "--bind", "0.0.0.0:8005", "--workers", "1", "--threads", "2", "app:app"]
