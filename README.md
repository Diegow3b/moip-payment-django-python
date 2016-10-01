### Project Under construction
## Version 0.1

## Dependencies
Django==1.10.1                                                                                                        
pycurl==7.43.0 

MoIP is a online payment system from Brazil
language - pt-br

Esse é um projeto para integração facil utilizando Django 1.10 e as API's do Moip (Envio[Xml], Processamento[JSON], Acompanhamento[NASP])
O processo é automatizado precisando apenas passar os dados e o modulo irá criar o seu pagamento, processar e preparar para o acompanhamento
Será necessário integrar a sua regra de negocio na views de notificacao (em construcao) para inserir a sua logica quando o moip realizar uma
alteração no seu pagamento. e enviar os dados que serão documentados para a funcao de criao e envio do pagamento

## Fixture
Rode esses scrips para carregar dados no seu banco
### Usuario
```sh
python manage.py loaddata user.json
```
### Formas de Pagamento
```sh
python manage.py loaddata forma_pagamento.json
```
## Autenticação
login: admin
password: admin123