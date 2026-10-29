# Primeiro estágio: Builder
FROM python:3.11-alpine AS builder

# Prevenir o python de gerar os arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1

RUN apk add --no-cache gcc musl-dev linux-headers

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Segundo estágio: Imagem pequena final
FROM python:3.11-alpine

# Forca os logs a aparecerem diretamente na console
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

RUN adduser -D -u 10001 appuser

WORKDIR /app

# Copiar o ambiente virtual do builder
COPY --from=builder /opt/venv /opt/venv

# Copiar o código da aplicação com a propriedade correta
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8003

CMD ["gunicorn", "--bind", "0.0.0.0:8003", "app:app"]
