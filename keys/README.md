# RSA ключи для JWT

- `private.pem` — приватный ключ (НЕ КОММИТИТЬ, хранить в секрете)
- `public.pem` — публичный ключ (можно коммитить, безопасен)

## Генерация ключей

```bash
# Приватный ключ
openssl genrsa -out private.pem 2048

# Публичный ключ
openssl rsa -in private.pem -pubout -out public.pem