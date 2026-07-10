# Payment service

Payment service принимает платежи через HTTP API, сохраняет их в PostgreSQL, пишет событие в outbox, публикует сообщение в RabbitMQ, обрабатывает его consumer-ом, обновляет статус платежа и отправляет webhook.

## Что реализовано

- REST API `/api/v1/payments`.
- Авторизация по `X-API-Key`.
- Идемпотентное создание платежа по `Idempotency-Key`.
- PostgreSQL + Alembic migrations.
- Outbox pattern.
- Отдельный `outbox_publisher`.
- RabbitMQ exchange/queues/retry/DLQ.
- Consumer обработки платежей.
- Retry с exponential backoff.
- Webhook sender.
- Unit, infrastructure и integration tests.

## Стек

- Python 3.13
- FastAPI
- SQLAlchemy async + asyncpg
- Alembic
- Dishka
- RabbitMQ + FastStream
- PostgreSQL
- Pytest

## Склонировать репозиторий:

```bash
git clone git@github.com:knriia/payments_service.git
cd payments_service
```
## Переменные окружения

В проекте есть файл с примером переменных окружения. Перед запуском нужно создать `.env` на его основе.

```bash
cp .env.example .env
```

## Запуск через Makefile

Собрать образы:

```bash
make build
```

Запустить сервисы:

```bash
make up
```

Посмотреть статус контейнеров:

```bash
make ps
```

Посмотреть логи всех сервисов:

```bash
make logs
```

Посмотреть логи конкретного сервиса:

```bash
make logs api
make logs outbox_publisher
make logs consumer
```

Зайти в контейнер:

```bash
make shell postgres
```

Остановить сервисы:

```bash
make down
```

Посмотреть все доступные команды:

```bash
make help
```

## Запуск без Makefile

Собрать образы:

```bash
docker compose build
```

Запустить сервисы:

```bash
docker compose up -d
```

Посмотреть статус контейнеров:

```bash
docker compose ps
```

Посмотреть логи всех сервисов:

```bash
docker compose logs -f
```

Посмотреть логи конкретного сервиса:

```bash
docker compose logs -f api
docker compose logs -f outbox_publisher
docker compose logs -f consumer
```

Зайти в контейнер:

```bash
docker compose exec api bash
```

Остановить сервисы:

```bash
docker compose down
```

## Доступные сервисы

API:

```text
http://localhost:8001
```

RabbitMQ Management UI:

```text
http://localhost:15672
```

## API

### Создать платеж

```bash
curl -X POST http://localhost:8001/api/v1/payments \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-secret-api-key" \
  -H "Idempotency-Key: payment-key-1" \
  -d '{
    "amount": "100.00",
    "currency": "RUB",
    "description": "test payment",
    "metadata": {"order_id": "order-1"},
    "webhook_url": "https://example.com/webhook"
  }'
```

### Получить платеж

```bash
curl http://localhost:8001/api/v1/payments/<payment_id> \
  -H "X-API-Key: dev-secret-api-key"
```

## Пример данных

Headers:

```text
X-API-Key: dev-secret-api-key
Idempotency-Key: payment-key-1
Content-Type: application/json
```

Body:

```json
{
  "amount": "100.00",
  "currency": "RUB",
  "description": "test payment",
  "metadata": {
    "order_id": "order-1"
  },
  "webhook_url": "https://example.com/webhook"
}
```

## Тесты

Для infrastructure и integration тестов нужна отдельная тестовая БД.

Запуск через Makefile:

```bash
make up postgres_test
pytest -q
```

Запуск без Makefile:

```bash
docker compose up -d postgres_test
pytest -q
```

Запустить только infrastructure tests:

```bash
pytest src/payments/infrastructure/tests -q
```

Запустить только integration flow:

```bash
pytest src/payments/tests/test_payment_flow.py -q
```
