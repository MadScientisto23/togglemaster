# Primeiro estágio: builder
FROM golang:1.23-alpine AS builder
WORKDIR /app
COPY . .
RUN go mod download
# Compilar o binário que será usado
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# Segundo estágio: imagem final leve
FROM alpine:latest
# Instalar os binarios para rodar comandos da aws-cli
RUN apk update && apk add --no-cache aws-cli

WORKDIR /
# Copia o código da aplicação do builder
COPY --from=builder /app/main .

EXPOSE 8004
CMD ["/main"]
