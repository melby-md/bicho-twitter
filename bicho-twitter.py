#!/usr/bin/env python3
# Jogo do Bicho Para o Twitter
# Copyright 2023 Pedro Debs <pedrodebs1@gmail.com>
# Licensed under the MIT License that can be found in the LICENSE file or at
# https://spdx.org/licenses/MIT.html
import argparse
import html.parser
import sys

import requests
import requests_oauthlib

bichos = (
    # Se um dia criarem um emoji de avestruz, use ele ao invés de um dodô
    ("avestruz", "🦤"),
    ("águia", "🦅"),
    # O emoji do burro ainda não é universalmente suportado, alguns editores de
    # texto não conseguem mostrar ele, por isso usar o código unicode
    ("burro", "\U0001FACF"), 
    ("borboleta", "🦋"),
    ("cachorro", "🐕"),
    ("cabra", "🐐"),
    ("carneiro", "🐏"),
    ("camelo", "🐫"),
    ("cobra", "🐍"),
    ("coelho", "🐇"),
    ("cavalo", "🐎"),
    ("elefante", "🐘"),
    ("galo", "🐓"),
    ("gato", "🐈"),
    ("jacaré", "🐊"),
    ("leão", "🦁"),
    ("macaco", "🐒"),
    ("porco", "🐖"),
    ("pavão", "🦚"),
    ("peru", "🦃"),
    ("touro", "🐂"),
    ("tigre", "🐅"),
    ("urso", "🐻"),
    ("veado", "🦌"),
    ("vaca", "🐄")
)

# Este parser faz o menor esforço possivel para extrair as informações
# necessárias, a informação em cada tag <td> fica guardada na matriz raw_data,
# exceto a coluna com "nº", e os campos <th> no cabeçalho referentes aos
# horários (PTM, PT, PTV...) ficam guardados no vetor schedule.
class Parser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()

        # A variavel tbody serve para saber ser o parser já passou pela tag
        # <tbody>, assim, evitando a criação de uma linha na matriz raw_data
        # para o cabeçalho da tabela porque ele reside na tag <thead>.
        self.tbody = False
        self.raw_data = []
        self.schedule = []

    def handle_starttag(self, tag, attrs):
        # A função handle_data precisa saber em qual tag estamos
        self.tag = tag

        # Início de uma nova linha na tabela, nova linha na matriz
        if tag == "tr" and self.tbody:
            self.raw_data.append([])

        elif tag == "tbody":
            self.tbody = True

    def handle_data(self, data):
        # Se o tamanho do conteúdo for igual a 2 quer dizer que é a coluna "nº",
        # logo, podemos ignorá-lo
        if self.tag == "td" and len(data) > 2:
            self.raw_data[-1].append(data)

        elif self.tag == "th":
            self.schedule.append(data)

def die(msg):
    sys.stderr.write(sys.argv[0] + ": Erro: " + msg + "\n")
    sys.exit(1)

# Obrigado python por tornar o getopt obsoleto, eu amo o argparse :)
# https://stackoverflow.com/questions/35847084/customize-argparse-help-message
class HelpFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        return super().add_usage(usage, actions, groups, "Uso: ")

argparser = argparse.ArgumentParser(add_help=False, formatter_class=HelpFormatter)
argparser.add_argument("-h", action="help", default=argparse.SUPPRESS, help="Mostra esta mensagem de ajuda e sai")
argparser.add_argument("-s", metavar="ARQUIVO", help="Especifica o arquivo com os segredos")
argparser.add_argument("-l", action="store_true", help="Imprime os resultados no terminal ao invés do Twitter")
argparser.add_argument("-f", metavar="ARQUIVO", help="Use uma cópia local do site")

argparser._optionals.title = "Opções"

args = argparser.parse_args()

if args.s is None and not args.l:
    die("Informe um arquivo de segredos")

if args.f is not None:
    with open(args.f, encoding="utf-8") as f:
        text = f.read()
else:
    # Resultados do Rio de Janeiro são válidos na maioria do Brasil.
    # Essa URL foi obtida apartir da engenharia reversa do applicativo:
    # https://play.google.com/store/apps/details?id=com.jdb.jogodobichoonline
    # Ela também é possivelmente usada na sequinte extensão:
    # https://chrome.google.com/webstore/detail/deu-no-poste-resultado-do/pmhahobhecijfkmlpkhcjddbifpheffo
    with requests.get(
        "https://www.eojogodobicho.com/jogo/get_resultados_hoje.php"
    ) as f:
        text = f.text

parser = Parser()
parser.feed(text)

# A classe Parser apenas extrai os dados brutos, cada horário preenche uma
# coluna na tabela, esse loop descobre o índice da ultima coluna preenchida (a
# mais recente), sendo a colluna vazia a que contem "0000-25", se ela não
# existir, a ultima coluna é usada
i = -1
for td in parser.raw_data[0]:
    if td.startswith("00"):
        break
    i += 1

if i == -1:
    die("Nenhum resultado hoje")

# Monta o texto final para ser enviado
n = 1
results = []
for row in parser.raw_data:
    # Os números apos a travessão representam o bicho
    l, r = row[i].split("-")
    name, emoji = bichos[int(r)-1]
    results.append(f"{n}º {l}-{r.rjust(2,'0')} {name} {emoji}")
    n += 1

final = parser.schedule[i] + "\n" + "\n".join(results)

if args.l:
    print(final)
    sys.exit(0)

with open(args.s) as secret_file:

    consumer_key = None
    consumer_secret = None
    access_token = None
    access_token_secret = None

    try:
        for record in secret_file:

            record = record.strip()

            if record.startswith("#") or len(record) == 0:
                continue

            key, value = record.split("=")
            key = key.strip()
            value = value.strip()

            if key == "consumer_key":
                consumer_key = value
            elif key == "consumer_secret":
                consumer_secret = value
            elif key == "access_token":
                access_token = value
            elif key == "access_token_secret":
                access_token_secret = value

    except ValueError:
        die(f"Formato do arquivo de segredos inválido: '{record}'")

if consumer_key is None:
    die("chave 'consumer_key' em falta")
elif consumer_secret is None:
    die("chave 'consumer_secret' em falta")
elif access_token is None:
    die("chave 'access_token' em falta")
elif access_token_secret is None:
    die("chave 'access_token_secret' em falta")

auth = requests_oauthlib.OAuth1(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)
requests.post(
    auth=auth,
    url="https://api.twitter.com/2/tweets",
    json={"text": final},
    headers={"Content-Type": "application/json"}
)
