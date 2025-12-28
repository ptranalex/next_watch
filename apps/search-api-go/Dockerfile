FROM golang:1.22-alpine AS builder

WORKDIR /app

COPY go.mod ./
RUN go mod download

COPY . ./

ARG VERSION=dev
ARG COMMIT=none

RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags "-s -w -X main.version=${VERSION} -X main.commit=${COMMIT}" -o /out/search-api ./cmd/search-api

FROM gcr.io/distroless/static-debian12:nonroot

WORKDIR /

COPY --from=builder /out/search-api /search-api

EXPOSE 8080

USER nonroot:nonroot

ENTRYPOINT ["/search-api"]
