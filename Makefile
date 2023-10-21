# Este makefile cria uma versão de release do binário, para uma versão de
# desenvolvimento use "go build"
GO = go
GOFLAGS = -trimpath -ldflags="-s -w"
CGO_ENABLED = 0

all: bicho-twitter

bicho-twitter: main.go go.mod go.sum
	CGO_ENABLED=$(CGO_ENABLED) $(GO) build $(GOFLAGS)

clean:
	rm -f bicho-twitter

.PHONY: clean
