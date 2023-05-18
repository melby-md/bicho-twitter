#!/usr/bin/env python3
# Jogo do Bicho Para o Twitter
# Copyright 2023 Pedro Debs <pedrodebs1@gmail.com>
# Licensed under the MIT license
# See the LICENSE file
import getopt
import html.parser
import sys

import requests
import tweepy

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

def help():
    print(f"""\
Uso: {sys.argv[0]} OPÇÕES
OPÇÕES:
  -h         mostra esta mensagem e sai imediatamente
  -s ARQUIVO especifica o arquivo com os segredos
  -l         imprime os resultados no terminal ao invés do Twitter
  -f ARQUIVO use uma cópia local do site""")
    sys.exit(0)

try:
    flags, args = getopt.getopt(sys.argv[1:], "hls:f:")

    # A CLI não aceita argumentos que não sejam flags
    if len(args) > 0:
        raise getopt.GetoptError("Opção inválida: " + " ".join(args))

except getopt.GetoptError as e:
    die(e.msg + "\nUse -h para ver a lista de opções")

opts = dict(flags)

if "-h" in opts:
    help()

secret_file_path = opts.get("-s")
if secret_file_path == None and "-l" not in opts:
    die("Informe um arquivo de segredos")

file_path = opts.get("-f")
if file_path is not None:
    f = open(file_path, "r", encoding="utf-8")
    text = f.read()
else:
    # Resultados do Rio de Janeiro são válidos na maioria do Brasil.
    # Essa URL foi obtida apartir da engenharia reversa do applicativo:
    # https://play.google.com/store/apps/details?id=com.jdb.jogodobichoonline
    # Ela também é possivelmente usada na sequinte extensão:
    # https://chrome.google.com/webstore/detail/deu-no-poste-resultado-do/pmhahobhecijfkmlpkhcjddbifpheffo
    f = requests.get(
        "https://www.eojogodobicho.com/jogo/get_resultados_hoje.php"
    )
    text = f.text
f.close()

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

if "-l" in opts:
    print(final)
    sys.exit(0)

# VARIAVEIS DE AMBIENTE NÃO SÃO SEGURAS PARA GUARDAR SENHAS/SEGREDOS EM UM
# AMBIENTE COMUM, talvez elas sejam em um container no contexto da nuvem, talvez
# um dia eu implemente essa funcionalidade...
# Formato do arquivo de segredos:
# nome_da_variavel=conteúdo
# sem espaços, aspas, linhas vazias ou comentários
if secret_file_path == "-":
    secret_file = sys.stdin
else:
    secret_file = open(secret_file_path, "r")

# Com certeza existe um jeito melhor de fazer isso
consumer_key = None
consumer_secret = None
access_token = None
access_token_secret = None

try:
    for record in secret_file:
        key, value = record.strip().split("=")
        if key == "consumer_key":
            consumer_key = value
        elif key == "consumer_secret":
            consumer_secret = value
        elif key == "access_token":
            access_token = value
        elif key == "access_token_secret":
            access_token_secret = value
        else:
            die(f"chave '{key}' inválida")
except ValueError:
    die("Formato do arquivo de segredos inválido")

if consumer_key is None:
    die("chave 'consumer_key' em falta")
elif consumer_secret is None:
    die("chave 'consumer_secret' em falta")
elif access_token is None:
    die("chave 'access_token' em falta")
elif access_token_secret is None:
    die("chave 'access_token_secret' em falta")

auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret
)
api = tweepy.API(auth)
api.update_status(final)
