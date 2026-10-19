# Use a valid Go version (1.23 is stable)
FROM golang:1.23-alpine

WORKDIR /app

# 1. Copy ALL your project files (including go.mod and main.go) into the container
COPY . .

# 2. Download your dependencies
RUN go mod download

EXPOSE 8004

# 3. Now "go run" will find your go.mod and code files perfectly!
CMD ["go", "run", "."]
