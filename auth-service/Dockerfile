FROM golang:1.23-alpine

WORKDIR /app

COPY . .

RUN go mod download

EXPOSE 8001

CMD ["go", "run", "."]
