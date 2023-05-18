#!/usr/bin/env python3
# Jogo do Bicho Para o Twitter
# Copyright 2023 Pedro Debs <pedrodebs1@gmail.com>
# Licensed under the MIT license
# See the LICENSE file
import getopt
import re
import sys

import requests
import tweepy

emojis = {
    # Se um dia criarem um emoji de avestruz, use ele ao invés de um dodo
    "AVESTRUZ": "🦤", 
    "ÁGUIA": "🦅",
    # O emoji do burro ainda não é universalmente suportado, alguns editores de
    # texto não conseguem mostrar ele, por isso usar o código unicode
    "BURRO": "\U0001FACF", 
    "BORBOLETA": "🦋",
    "CACHORRO": "🐕",
    "CABRA": "🐐",
    "CARNEIRO": "🐏",
    "CAMELO": "🐫",
    "COBRA": "🐍",
    "COELHO": "🐇",
    "CAVALO": "🐎",
    "ELEFANTE": "🐘",
    "GALO": "🐓",
    "GATO": "🐈",
    "JACARÉ": "🐊",
    "LEÃO": "🦁",
    "MACACO": "🐒",
    "PORCO": "🐖",
    "PAVÃO": "🦚",
    "PERU": "🦃",
    "TOURO": "🐂",
    "TIGRE": "🐅",
    "URSO": "🐻",
    "VEADO": "🦌",
    "VACA": "🐄"
}

schedule = {
    11: "PTM",
    14: "PT",
    16: "PTV",
    18: "PTN",
    19: "FED",
    21: "COR"
}

def die(msg):
    sys.stderr.write(msg + '\n')
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
        raise getopt.GetoptError(f"Opção inválida: '{' '.join(args)}'")

except getopt.GetoptError as e:
    sys.stderr.write(f"{sys.argv[0]}: Erro: {e.msg}\n")
    die("Use -h para ver a lista de opções")

opts = dict(flags)

if "-h" in opts:
    help()

secret_file_path = opts.get("-s")
if secret_file_path == None and "-l" not in opts:
    die("Informe um arquivo de segredos")

file_path = opts.get("-f")
if file_path is not None:
    f = open(file_path, 'r', encoding="utf-8")
    lines = f
else:
    # Resultados do Rio de Janeiro são válidos na maioria do Brasil
    f = requests.get(
        "https://portalbrasil.net/jogodobicho/resultado-do-jogo-do-bicho/",
        headers={'User-agent': 'Chrome/113.0.0.0'}
    )
    lines = f.iter_lines(decode_unicode=True)

hours_regex = re.compile("das ([0-9]{2})")
for line in lines:
    if line.startswith("<h3>"):
        hours = int(re.search(hours_regex, line).group(1))
    if line.startswith("***"):
        break

results = []

regex = re.compile(r"g>(.*)</st")
for line in lines:

    if line.startswith("<h"):
        break

    m = re.search(regex, line)
    if m == None:
        continue

    beg, animal = m.group(1) \
        .replace(" ►", "") \
        .replace("\u00A0", "") \
        .replace(" &#8211; ", "-") \
        .split(" &#8212; ")

    if animal == "LEAO":
        animal = "LEÃO"

    emoji = emojis[animal]
    results.append(f"{beg} {animal.lower()} {emoji}")

f.close()

if len(results) == 0:
    die("Deu ruim")

final = schedule[hours] + "\n" + "\n".join(results)

if "-l" in opts:
    print(final)
    sys.exit(0)

# VARIAVEIS DE AMBIENTE NÃO SÃO SEGURAS PARA GUARDAR SENHAS/SEGREDOS EM UM
# AMBIENTE COMUM, talvez elas sejam em um container no contexto da nuvem, talvez
# um dia eu implemente essa funcionalidade...
# Formato do aqruivo de segredos:
# nome_da_variavel=conteúdo
# sem espaços, aspas, linhas vazias ou comentários
if secret_file_path == '-':
    secret_file = sys.stdin
else:
    secret_file = open(secret_file_path, 'r')

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
