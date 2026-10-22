FROM golang:1.23-alpine

RUN apk update && apk add --no-cache aws-cli

WORKDIR /app

COPY . .

RUN go mod download

EXPOSE 8004

CMD ["go", "run", "."]
