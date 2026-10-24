# Primeio estagio build do binario
FROM golang:1.23-alpine AS builder
WORKDIR /app
COPY . .
RUN go mod download
# Compilar um binario estatico
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# Segundo estagio: Cria uma imagem leve
FROM scratch
WORKDIR /
# Copiar somente o binario compilado do builder
COPY --from=builder /app/main .
EXPOSE 8001
CMD ["/main"]
