# Jogo do Bicho Para o Twitter

Um bot que posta os resultados do jogo do bicho do Rio de Janeiro no Twitter
usando a API v2, criado para operar a conta 
[@o\_jogo\_do\_bicho](https://twitter.com/o_jogo_do_bicho), mas o código pode
ser facilmente modificado para enviar os resultados do jogo do bicho para aonde
você quiser.

**AVISO: O Jogo do Bicho é ilegal no Brasil, participar nele se configura como
uma contravenção penal de acordo com o artigo 50 do Decreto-lei nº 3.688, de 3
de outubro de 1941. Nem os autores e nem os contribuintes deste software
endossam qualquer tipo de atividade ilegal ou prática de jogo de azar, este
software tem a finalidade de meramente reproduzir dados públicos obtidos por
meio da internet para fins educativos.**

## Deployment

É recomendavel criar um usuário separado para o deployment, `_bicho`, por
exemplo

    adduser -s /sbin/nologin _bicho

Copie os arquivos do programa para a home do novo usuário.

    git clone --depth=1 https://github.com/melby-md/jogo-do-bicho-twitter.git /home/_bicho/src

### Dependências

* Alguma implementação do `cron`.
* Python, versão 3.8, no mínimo.

Bibliotecas python:

* requests
* requests\_oauthlib

O arquivo `requirements.txt` tem versões exatas das bibliotecas testadas.

Você pode instalar as bibliotecas do jeito que você quiser, mas, eu recomendo
um [ambiente virtual](https://docs.python.org/3/library/venv.html).

    cd /home/_bicho/
    python -m venv env
    ./env/bin/python -m pip install -r src/requirements.txt

E se certifique que todos esses aruivos sejam do usuário certo

    chown -R _bicho:_bicho /home/_bicho

### Arquivo de segredos

Crie um aquivo para quardar as chaves para o seu app criado no portal de
desenvolvedores do twitter, `segredos.txt`, por exemplo, e antes de inserir algo
nele, mude as permições para que apenas o dono possa ler e escrever nele:

    touch segredos.txt
    chown _bicho:_bicho segredos.txt
    chmod 600 segredos.txt

O formato do arquivo é:

    nome_da_chave=valor

comentários podem ser postos em sua própria linha e começam com `#`

As chaves necessárias são:

* consumer\_key
* consumer\_secret
* access\_token
* access\_token\_secret

### Cronjobs

Adicione o conteúdo de `crontab` ao crontab do usuário, modifique ele e o script
`bicho-wrapper.sh` de acordo com a localização dos aqruivos e o caminho do
binário do python. Os horários em `crontab` estão no horário de Brasília, caso o
seu sistema esteja em outro fuso horário, modifique de acordo.

    crontab -u _bicho src/crontab # isso vai apagar o crontab desse usuário

## Licença

Copyright 2023 Pedro Debs &lt;<pedrodebs1@gmail.com>&gt;

Jogo do Bicho Para o Twitter é licenciado sob a licença MIT (Veja o
arquivo `LICENSE` ou <https://spdx.org/licenses/MIT.html>).

