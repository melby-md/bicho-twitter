# Jogo do Bicho Para o Twitter

Um bot escrito em go que posta os resultados do jogo do bicho do Rio de Janeiro
no Twitter usando a API v2, criado para operar a conta 
[@o\_jogo\_do\_bicho](https://twitter.com/o_jogo_do_bicho), mas o código pode
ser facilmente modificado para enviar os resultados do jogo do bicho para aonde
você quiser.

uma versão de python pode ser encontrada no commit
[a8499de63d](https://github.com/melby-md/bicho-twitter/tree/a8499de63d77e86e031d11de0b9badfdc26de917)
para traz.

**AVISO: O Jogo do Bicho é ilegal no Brasil, participar nele se configura como
uma contravenção penal de acordo com o artigo 50 do Decreto-lei nº 3.688, de 3
de outubro de 1941. Nem os autores e nem os contribuintes deste software
endossam qualquer tipo de atividade ilegal ou prática de jogo de azar, este
software tem a finalidade de meramente reproduzir dados públicos obtidos por
meio da internet para fins educativos.**

## Build

Para compilar é necessário o compilador de go (versão 1.19, no mínimo), e para
rodar apenas precisa de uma implementação do `cron` caso você queira rodar
periodicamente.

Para compilar uma versão release:

    make

caso você não tenha o `make`:

    CGO_ENABLED=0 go build -trimpath -ldflags="-s -w"

Isso vair criar o binário `bicho-twitter` (estaticamente linkado) ou
`bicho-twitter.exe` no Windows

Para rodar sem postar no Twitter:

    bicho-twitter -l

## Arquivo de segredos

Para poder postar os resultados no Twitter é necessário um arquivo para guardar
[os tokens do seu app criado no portal de desenvolvedores do Twitter](https://developer.twitter.com/en/docs/apps/overview)
, vou usar `segredos.txt` como exemplo, é recomendavel limitar o acesso a esse
arquivo antes de escrever nele se você estiver em um sistema \*NIX
(principalmente se for em um abiente de produção):

    touch segredos.txt
    chmod 600 segredos.txt

O formato do arquivo é:

    nome_da_chave=valor

comentários podem ser postos em sua própria linha e começam com `#`

As chaves necessárias são:

* `consumer_key`
* `consumer_secret`
* `access_token`
* `access_token_secret`

## Rodando como um cronjob

É recomendavel criar um usuário separado para o deployment, `_bicho`, por
exemplo

    adduser -s /sbin/nologin _bicho

Adicione o conteúdo de `crontab` ao crontab do usuário, modifique ele de acordo
com a localização do executavel e do arquivo de segredos. Os horários em
`crontab` estão no horário de Brasília (UTC-3), caso o seu sistema esteja em
outro fuso horário, modifique de acordo.

    crontab -u _bicho src/crontab # isso vai apagar o crontab desse usuário

## Copyright

Copyright 2023 Pedro Debs &lt;<pedrodebs1@gmail.com>&gt;

Jogo do Bicho Para o Twitter é licenciado sob a licença MIT (Veja o
arquivo `LICENSE`).

