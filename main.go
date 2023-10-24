/* Jogo do Bicho Para o Twitter
 * Copyright 2023 Pedro Debs <pedrodebs1@gmail.com>
 * Licenciado sob a licença MIT (veja o arquivo LICENSE)
 */
package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"github.com/dghubble/oauth1"
	"golang.org/x/net/html"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
)

func main() {
	bichos := [...]string{
		// Se um dia criarem um emoji de avestruz, use ele ao invés de um dodô
		"avestruz 🦤",
		"águia 🦅",
		// O emoji do burro ainda não é universalmente suportado, alguns editores de
		// texto não conseguem mostrar ele, por isso usar o código unicode
		"burro \U0001FACF",
		"borboleta 🦋",
		"cachorro 🐕",
		"cabra 🐐",
		"carneiro 🐏",
		"camelo 🐫",
		"cobra 🐍",
		"coelho 🐇",
		"cavalo 🐎",
		"elefante 🐘",
		"galo 🐓",
		"gato 🐈",
		"jacaré 🐊",
		"leão 🦁",
		"macaco 🐒",
		"porco 🐖",
		"pavão 🦚",
		"peru 🦃",
		"touro 🐂",
		"tigre 🐅",
		"urso 🐻",
		"veado 🦌",
		"vaca 🐄",
	}

	log.SetPrefix("Erro: ")
	log.SetFlags(0)

	help := flag.Bool("h", false, "Mostra esta mensagem de ajuda e sai")
	local := flag.Bool("l", false, "Imprime os resultados no terminal ao invés do Twitter")
	secrets_file_path := flag.String("s", "", "Especifica o arquivo com os segredos")
	local_copy := flag.String("f", "", "Usa uma cópia local do site")
	flag.Parse()

	if *help {
		fmt.Fprintf(os.Stderr, `Uso: %s [OPÇÔES]
OPÇÕES:
   -h         Mostra esta mensagem de ajuda e sai
   -l         Imprime os resultados no terminal ao invés do Twitter
   -s ARQUIVO Especifica o arquivo com os segredos
   -f AQRUIVO Usa uma cópia local do site
`, os.Args[0])
		os.Exit(0)
	}

	if !*local && *secrets_file_path == "" {
		log.Fatal("Arquivo de segredos em falta")
	}

	var file io.ReadCloser
	var err error

	if *local_copy == "" {
		// Resultados do Rio de Janeiro são válidos na maioria do Brasil.
		// Essa URL foi obtida apartir da engenharia reversa do applicativo:
		// https://play.google.com/store/apps/details?id=com.jdb.jogodobichoonline
		// Ela também é possivelmente usada na sequinte extensão:
		// https://chrome.google.com/webstore/detail/deu-no-poste-resultado-do/pmhahobhecijfkmlpkhcjddbifpheffo
		resp, err := http.Get("https://www.eojogodobicho.com/jogo/get_resultados_hoje.php")
		if err != nil {
			log.Fatal(err)
		}

		file = resp.Body
	} else {
		file, err = os.Open(*local_copy)
		if err != nil {
			log.Fatal(err)
		}
	}
	defer file.Close()

	// A primeira fase do parsing extrai os dados brutos, os resultados
	// ficam guardados na matriz data e o nome de cada horário fica no
	// vetor sched
	tkn := html.NewTokenizer(file)

	var data [5][7]string
	var sched [5]string

	data_x := 0
	data_y := 0
	sched_i := 0
	is_thead := false
	is_tbody := false

	for tt := tkn.Next(); tt != html.ErrorToken; tt = tkn.Next() {
		switch tt {
		case html.StartTagToken:
			t := tkn.Token().Data
			if t == "tbody" {
				is_tbody = true
			} else if t == "thead" {
				is_thead = true
			}

		case html.TextToken:
			text := tkn.Token().Data
			if is_tbody {
				if len(text) > 3 {
					data[data_x][data_y] = text
					data_x++
				}
			} else if is_thead {
				sched[sched_i] = text
				sched_i++
			}

		case html.EndTagToken:
			if is_tbody && tkn.Token().Data == "tr" {
				data_y++
				data_x = 0
			}
		}
	}

	// Descobre a coluna com os resultados mais recentes
	i := -1
	for _, column := range data {
		if column[0] == "" || strings.HasPrefix(column[0], "00") {
			break
		}
		i++
	}

	if i == -1 {
		log.Fatal("Nenhum resultado hoje")

	}

	// Criação da string final
	s := [8]string{sched[i]}

	for n, row := range data[i] {
		n += 1
		split := strings.SplitAfter(row, "-")
		bicho_i, _ := strconv.Atoi(split[1])
		bicho := bichos[bicho_i-1]
		s[n] = fmt.Sprintf("%dº %s%02d %s", n, split[0], bicho_i, bicho)
	}

	final := strings.Join(s[:], "\n")
	if *local {
		fmt.Println(final)
		os.Exit(0)
	}

	// Parte que lida com o Twitter

	secrets_file, err := os.Open(*secrets_file_path)
	if err != nil {
		log.Fatal(err)
	}
	defer secrets_file.Close()

	scanner := bufio.NewScanner(secrets_file)

	var consumer_key string
	var consumer_secret string
	var access_token string
	var access_token_secret string

	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())

		if len(line) == 0 || line[0] == '#' {
			continue
		}

		split := strings.SplitN(line, "=", 2)

		if len(split) == 1 {
			log.Fatalf("Formato do arquivo de segredos inválido: '%s'", line)
		}

		key := strings.TrimSpace(split[0])
		value := strings.TrimSpace(split[1])

		switch key {
		case "consumer_key":
			consumer_key = value
		case "consumer_secret":
			consumer_secret = value
		case "access_token":
			access_token = value
		case "access_token_secret":
			access_token_secret = value
		}
	}
	if consumer_key == "" {
		log.Fatal("chave 'consumer_key' em falta")
	} else if consumer_secret == "" {
		log.Fatal("chave 'consumer_secret' em falta")
	} else if access_token == "" {
		log.Fatal("chave 'access_token' em falta")
	} else if access_token_secret == "" {
		log.Fatal("chave 'access_token_secret' em falta")
	}

	config := oauth1.NewConfig(consumer_key, consumer_secret)
	token := oauth1.NewToken(access_token, access_token_secret)

	httpClient := config.Client(oauth1.NoContext, token)

	json_str, _ := json.Marshal(map[string]string{"text": final})
	resp, err := httpClient.Post("https://api.twitter.com/2/tweets", "application/json", bytes.NewReader(json_str))

	if err != nil {
		log.Fatal(err)
	}

	if resp.StatusCode != 201 {
		log.Fatal(resp.Status)
	}
}
