# -*- coding: utf-8 -*-
from django.shortcuts import render

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext

from moip.models import Moip

# Create your views here.
def testador_moip(request):
    # ---- Dados de Teste com os Respectivos Formatos ----- #
    tipo_periocidade = None # 'Mensal'
    quantidade_periocidade = None # '2'
    valor = '7777'
    tipo_pagamento = 'InstrucaoUnica'    
    pagador_nome = 'Diego'
    pagador_email = 'diegoteste@msn.com'
    pagador_id = '123'
    pagador_endereco = 'Minha Rua'
    pagador_numero = "15"
    pagador_complemento = 'Complemento'
    pagador_bairro = 'Meu bairro'
    pagador_cidade = 'Salvador'
    pagador_estado = 'BA'
    pagador_pais = 'BRA'
    pagador_cep = '40130160'
    pagador_telefone = '(71)99887766'
    parcela_minima = "2"
    parcela_maxima = "12"
    pagamento_id = "codigo_unico_gerado_para_pagamento_123" # Opcional
    todos_moip = Moip.objects.all()
    if todos_moip:
        moip = todos_moip[0]
    else:
        raise ValidationError("É preciso criar uma configuração moip no admin")
    # ----- Nomenclatura que o XML espera receber ----- #
    xml = moip.construir_xml(
        tipo_periocidade = tipo_periocidade,
        quantidade_periocidade = quantidade_periocidade,
        valor = valor,
        tipo_pagamento = tipo_pagamento,
        pagador_nome = pagador_nome,
        pagador_email = pagador_email,
        pagador_id = pagador_id,
        pagador_endereco = pagador_endereco,
        pagador_numero = pagador_numero,
        pagador_complemento = pagador_complemento,
        pagador_bairro = pagador_bairro,
        pagador_cidade = pagador_cidade,
        pagador_estado = pagador_estado,
        pagador_pais = pagador_pais,
        pagador_cep = pagador_cep,
        pagador_telefone = pagador_telefone,
        parcela_minima = parcela_minima,
        parcela_maxima = parcela_maxima,
        #id = pagamento_id
    )
    
    response = moip.enviar_xml(xml)

    context = {
        'response': response,
        'xml': xml,
        'request': request,
    }

    return render(request, 'moip/index.html', context)
