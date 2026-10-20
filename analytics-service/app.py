import os
import sys
import threading
import json
import uuid
import time
import logging

import boto3
from botocore.exceptions import (
    NoCredentialsError,
    ClientError,
    EndpointConnectionError
)
from flask import Flask, jsonify
from dotenv import load_dotenv


# ============================================================
# LOGS E CONFIGURAÇÕES
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

log = logging.getLogger(__name__)

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SQS_QUEUE_URL = os.getenv("AWS_SQS_URL")
DYNAMODB_TABLE_NAME = os.getenv("AWS_DYNAMODB_TABLE")
DYNAMODB_ENDPOINT_URL = os.getenv("DYNAMODB_ENDPOINT_URL")

if not DYNAMODB_TABLE_NAME:
    log.critical("AWS_DYNAMODB_TABLE deve ser definida.")
    sys.exit(1)

if not SQS_QUEUE_URL:
    log.warning(
        "AWS_SQS_URL não foi definida. "
        "O worker SQS ficará desabilitado no ambiente local."
    )


# ============================================================
# CLIENTES AWS / DYNAMODB LOCAL
# ============================================================

try:
    session = boto3.Session(region_name=AWS_REGION)

    dynamodb_client = session.client(
        "dynamodb",
        endpoint_url=DYNAMODB_ENDPOINT_URL or None
    )

    sqs_client = None

    if SQS_QUEUE_URL:
        sqs_client = session.client("sqs")
        log.info("Cliente SQS inicializado.")

    log.info(
        "Cliente DynamoDB inicializado. Endpoint: %s",
        DYNAMODB_ENDPOINT_URL or "AWS"
    )

except NoCredentialsError:
    log.critical(
        "Credenciais AWS não encontradas. Verifique as variáveis de ambiente."
    )
    sys.exit(1)

except Exception as error:
    log.critical(
        "Erro ao inicializar os clientes AWS: %s",
        error
    )
    sys.exit(1)


# ============================================================
# PREPARAÇÃO DO DYNAMODB LOCAL
# ============================================================

def ensure_local_dynamodb_table():
    """Cria automaticamente a tabela quando usamos DynamoDB Local."""

    if not DYNAMODB_ENDPOINT_URL:
        log.info(
            "DynamoDB AWS configurado. "
            "A tabela deve ser criada pela infraestrutura."
        )
        return

    max_attempts = 10

    for attempt in range(1, max_attempts + 1):
        try:
            dynamodb_client.describe_table(
                TableName=DYNAMODB_TABLE_NAME
            )

            log.info(
                "Tabela DynamoDB '%s' já existe.",
                DYNAMODB_TABLE_NAME
            )

            return

        except dynamodb_client.exceptions.ResourceNotFoundException:
            log.info(
                "Criando a tabela DynamoDB Local '%s'...",
                DYNAMODB_TABLE_NAME
            )

            dynamodb_client.create_table(
                TableName=DYNAMODB_TABLE_NAME,
                AttributeDefinitions=[
                    {
                        "AttributeName": "event_id",
                        "AttributeType": "S"
                    }
                ],
                KeySchema=[
                    {
                        "AttributeName": "event_id",
                        "KeyType": "HASH"
                    }
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 1,
                    "WriteCapacityUnits": 1
                }
            )

            waiter = dynamodb_client.get_waiter("table_exists")

            waiter.wait(
                TableName=DYNAMODB_TABLE_NAME
            )

            log.info(
                "Tabela local '%s' criada com sucesso.",
                DYNAMODB_TABLE_NAME
            )

            return

        except (EndpointConnectionError, ClientError) as error:
            if attempt == max_attempts:
                log.critical(
                    "Não foi possível preparar o DynamoDB Local: %s",
                    error
                )
                raise

            log.warning(
                "DynamoDB Local ainda não está disponível. "
                "Tentativa %d de %d.",
                attempt,
                max_attempts
            )

            time.sleep(2)


ensure_local_dynamodb_table()


# ============================================================
# PROCESSAMENTO DAS MENSAGENS SQS
# ============================================================

def process_message(message):
    """Processa uma mensagem do SQS e grava no DynamoDB."""

    try:
        log.info(
            "Processando mensagem ID: %s",
            message["MessageId"]
        )

        body = json.loads(message["Body"])

        event_id = str(uuid.uuid4())

        item = {
            "event_id": {
                "S": event_id
            },
            "user_id": {
                "S": body["user_id"]
            },
            "flag_name": {
                "S": body["flag_name"]
            },
            "result": {
                "BOOL": body["result"]
            },
            "timestamp": {
                "S": body["timestamp"]
            }
        }

        dynamodb_client.put_item(
            TableName=DYNAMODB_TABLE_NAME,
            Item=item
        )

        log.info(
            "Evento %s da flag '%s' salvo no DynamoDB.",
            event_id,
            body["flag_name"]
        )

        sqs_client.delete_message(
            QueueUrl=SQS_QUEUE_URL,
            ReceiptHandle=message["ReceiptHandle"]
        )

    except json.JSONDecodeError:
        log.error(
            "JSON inválido na mensagem ID: %s",
            message.get("MessageId")
        )

    except ClientError as error:
        log.error(
            "Erro AWS ao processar a mensagem: %s",
            error
        )

    except Exception as error:
        log.error(
            "Erro inesperado ao processar a mensagem: %s",
            error
        )


def sqs_worker_loop():
    """Consulta continuamente a fila SQS."""

    log.info("Iniciando o worker SQS...")

    while True:
        try:
            response = sqs_client.receive_message(
                QueueUrl=SQS_QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20
            )

            messages = response.get("Messages", [])

            if not messages:
                continue

            log.info(
                "Recebidas %d mensagens.",
                len(messages)
            )

            for message in messages:
                process_message(message)

        except ClientError as error:
            log.error(
                "Erro AWS durante a leitura da fila SQS: %s",
                error
            )

            time.sleep(10)

        except Exception as error:
            log.error(
                "Erro inesperado no worker SQS: %s",
                error
            )

            time.sleep(10)


# ============================================================
# API DE HEALTH CHECK
# ============================================================

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "analytics-service",
        "sqs_worker": "enabled" if SQS_QUEUE_URL else "disabled",
        "dynamodb": (
            DYNAMODB_ENDPOINT_URL
            if DYNAMODB_ENDPOINT_URL
            else "aws"
        )
    })


# ============================================================
# INICIALIZAÇÃO DO WORKER
# ============================================================

def start_worker():
    """Inicia o worker somente quando existe uma fila configurada."""

    if not SQS_QUEUE_URL or sqs_client is None:
        log.warning(
            "Worker SQS desabilitado. "
            "O endpoint /health continuará disponível."
        )

        return

    worker_thread = threading.Thread(
        target=sqs_worker_loop,
        daemon=True
    )

    worker_thread.start()

    log.info("Worker SQS iniciado com sucesso.")


start_worker()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8005))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )