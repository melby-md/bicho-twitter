# Este makefile cria uma versão de release do binário, para uma versão de
# desenvolvimento use "go build"
GO = go
GOFLAGS = -trimpath -ldflags="-s -w"
CGO_ENABLED = 0

Windows_NT = .exe

all: bicho-twitter$($(OS))

bicho-twitter bicho-twitter.exe: main.go go.mod go.sum
	CGO_ENABLED=$(CGO_ENABLED) $(GO) build $(GOFLAGS)

clean:
	rm -f bicho-twitter bicho-twitter.exe

.PHONY: clean
