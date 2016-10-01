# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET

import pycurl
import base64

from django.db import models
from django.core.validators import URLValidator

# Create your models here.
class RespostaMoIP:
    conteudo = ''
    codigo = ''
    status = ''
    token = ''

    def __unicode__(self):
        return "Moip Response"
    
    def __init__(self):
        self.conteudo = ''
        self.codigo = ''
        self.status = ''
        self.token = ''

    def callback(self,buf):
        self.conteudo = buf
        root = ET.fromstring(buf)
        token = root.findall(".")
        child_resposta = token[0]._children[0]
        child_codigo = child_resposta._children[0]
        child_status = child_resposta._children[1]
        child_token = child_resposta._children[2]
        self.codigo = child_codigo.text
        self.status = child_status.text
        self.token = child_token.text

# Para Forma de pagamento favor chegar a referencia no moip
class FormaPagamento(models.Model):    
    descricao = models.CharField(max_length=100) # Campo de Apresentacao
    key = models.CharField(max_length=10) # Campo de referencia para o Moip
    def __unicode__(self):
        return self.descricao

class Moip(models.Model):
    # Modelo Administrativo para facil acesso na troca de instancias pelo admin
    titulo = models.CharField(max_length=100)
    apelido = models.CharField(max_length=100)
    razao = models.CharField(max_length=100)
    login_moip = models.CharField(max_length=100)
    boleto_imagem = models.FileField(null=True, blank=True, upload_to='uploads/moip/img/')
    url_notificacao = models.CharField(null=True, blank=True, max_length=100, validators=[URLValidator()])
    url_retorno = models.CharField(max_length=100, validators=[URLValidator()])
    url_ambiente = models.TextField(max_length=2000, validators=[URLValidator()])
    token_moip = models.CharField(max_length=200)
    key_moip = models.CharField(max_length=200)
    moeda = models.CharField(max_length=3, default="BRL")
    formas_pagamento = models.ManyToManyField(FormaPagamento, related_name="formas_pagamento")

    def __unicode__(self):
        return self.razao

    def enviar_xml(self, xml):
        try:   
            curl = pycurl.Curl()

            response = RespostaMoIP()
            passwd = "{0}:{1}".format(self.token_moip, self.key_moip)
            passwd64 = base64.b64encode(passwd)
            
            curl.setopt(pycurl.URL,self.url_ambiente)
            curl.setopt(pycurl.HTTPHEADER,["Authorization: Basic "+passwd64])
            curl.setopt(pycurl.USERAGENT,"Mozilla/4.0")
            curl.setopt(pycurl.USERPWD,passwd)
            curl.setopt(pycurl.POST,True)
            curl.setopt(pycurl.POSTFIELDS,xml)
            curl.setopt(pycurl.WRITEFUNCTION,response.callback)
            
            curl.perform()
            
        except Exception as e:
            print e
        finally:
            curl.close()

        return response

    def construir_xml(self, **kwargs):
        # --- Seguir determinados parametros para a construcao do xml --- #
        # -- Parametros obrigatórios -- #
        # Obs.: Razao tambem é obrigario mas nesse caso ele vem da referencia do objeto no self
        id_proprio = kwargs.pop('id', None)
        valor = kwargs.pop('valor', None) 
        tipo_pagamento = kwargs.pop('tipo_pagamento', None)
         # -- Usado para Pagamentos Recorrentes
        tipo_periocidade = kwargs.pop('tipo_periocidade', None)
        quantidade_periocidade = kwargs.pop('quantidade_periocidade', None)
        # -- Pagador - Uma vez definido o pagador o resto dos campos de pagadores todos sao obrigatorios
        # com exceção de complemento
        pagador_nome = kwargs.pop('pagador_nome', None)
        pagador_email = kwargs.pop('pagador_email', None)
        pagador_id = kwargs.pop('pagador_id', None)
        pagador_endereco = kwargs.pop('pagador_endereco', None)
        pagador_numero = kwargs.pop('pagador_numero', None)
        pagador_complemento = kwargs.pop('pagador_complemento', None)
        pagador_bairro = kwargs.pop('pagador_bairro', None)
        pagador_cidade = kwargs.pop('pagador_cidade', None)
        pagador_estado = kwargs.pop('pagador_estado', None)
        pagador_pais = kwargs.pop('pagador_pais', None)
        pagador_cep = kwargs.pop('pagador_cep', None)
        pagador_telefone = kwargs.pop('pagador_telefone', None)
        # -- Definir regras de parcelas, para mais informações como controle de juros cem cada parcela
        # acessar a documentação do moip
        parcela_minima = kwargs.pop('parcela_minima', None)
        parcela_maxima = kwargs.pop('parcela_maxima', None)
        # Mensagem de identificacao do pagamento
        mensagem = kwargs.pop('mensagem', None)
        
        if valor:
            valor = str(valor.replace(',','.'))
        # ----- Corpo Inicial ----- #
        node_enviar_instrucao = Element('EnviarInstrucao')
        # ----- Campos Obrigatórios ----- #
        if tipo_pagamento == 'InstrucaoRecorrente':
            node_instrucao = SubElement(node_enviar_instrucao, 'InstrucaoRecorrente')
            node_periocidade = SubElement(node_instrucao, 'Periodicidade', {'Tipo': tipo_periocidade})
            node_periocidade.text = quantidade_periocidade
        else:
            node_instrucao = SubElement(node_enviar_instrucao, 'InstrucaoUnica')
        
        node_razao = SubElement(node_instrucao, 'Razao')
        node_razao.text = self.razao
        node_valores = SubElement(node_instrucao, 'Valores')
        node_valor = SubElement(node_valores, 'Valor', {'Moeda':self.moeda})
        node_valor.text = valor
        if id_proprio:
            node_id_proprio = SubElement(node_instrucao, 'IdProprio')
            node_id_proprio.text = id_proprio
        # ----- Configuração do Recebedor ----- #
        node_recebedor = SubElement(node_instrucao, 'Recebedor')
        node_login_moip = SubElement(node_recebedor, 'LoginMoIP')
        node_login_moip.text = self.login_moip
        node_apelido = SubElement(node_recebedor, 'Apelido')
        node_apelido.text = self.apelido
        # ----- Configuração do Pagador ----- #
        node_pagador = SubElement(node_instrucao, 'Pagador')
        node_nome = SubElement(node_pagador, 'Nome')
        node_nome.text = pagador_nome
        node_email = SubElement(node_pagador, 'Email')
        node_email.text = pagador_email
        node_id_pagador = SubElement(node_pagador, 'IdPagador')
        node_id_pagador.text = pagador_id        
        node_endereco_cobranca = SubElement(node_pagador, 'EnderecoCobranca')
        node_logradouro = SubElement(node_endereco_cobranca, 'Logradouro')
        node_logradouro.text = pagador_endereco
        node_numero = SubElement(node_endereco_cobranca, 'Numero')
        node_numero.text = pagador_numero
        if pagador_complemento:
            node_complemento = SubElement(node_endereco_cobranca, 'Complemento')
            node_complemento.text = pagador_complemento
        node_bairro = SubElement(node_endereco_cobranca, 'Bairro')
        node_bairro.text = pagador_bairro
        node_cidade = SubElement(node_endereco_cobranca, 'Cidade')
        node_cidade.text = pagador_cidade
        node_estado = SubElement(node_endereco_cobranca, 'Estado')
        node_estado.text = pagador_estado
        node_pais = SubElement(node_endereco_cobranca, 'Pais')
        node_pais.text = pagador_pais
        node_cep = SubElement(node_endereco_cobranca, 'CEP')
        node_cep.text = pagador_cep
        node_telefone_fixo = SubElement(node_endereco_cobranca, 'TelefoneFixo')
        node_telefone_fixo.text = pagador_telefone 
        
        formas = self.formas_pagamento.all()
        # ----- Formas de Pagamento ----- #
        node_formas_pagamento = SubElement(node_instrucao, 'FormasPagamento')
        if formas.filter(key__exact='BoletoBancario'):
            forma_pagamento = SubElement(node_formas_pagamento, 'FormaPagamento')
            forma_pagamento.text = 'BoletoBancario'
        if formas.filter(key__exact='CartaoDeCredito'):
            forma_pagamento2 = SubElement(node_formas_pagamento, 'FormaPagamento')
            forma_pagamento2.text = 'CartaoDeCredito'
        if formas.filter(key__exact='CartaoDeDebito'):
            forma_pagamento3 = SubElement(node_formas_pagamento, 'FormaPagamento')
            forma_pagamento3.text = 'CartaoDeDebito'
        if formas.filter(key__exact='FinanciamentoBancario'):
            forma_pagamento4 = SubElement(node_formas_pagamento, 'FormaPagamento')
            forma_pagamento4.text = 'FinanciamentoBancario'
        if formas.filter(key__exact='CarteiraMoIP'):
            forma_pagamento5 = SubElement(node_formas_pagamento, 'FormaPagamento')
            forma_pagamento5.text = 'CarteiraMoIP'
        
        # --- Usados penas na Instrução Unica --- #
        if formas.filter(key__exact='CartaoCredito'):
            forma_pagamento6 = SubElement(node_formas_pagamento, 'FormaPagamento')
            forma_pagamento6.text = 'CartaoCredito'
        if formas.filter(key__exact='CartaoDebito'):
            forma_pagamento7 = SubElement(node_formas_pagamento, 'FormaPagamento')
            forma_pagamento7.text = 'CartaoDebito'
        
        # ----- Parcelamento ----- #
        if parcela_minima and parcela_maxima:
            node_parcelamentos = SubElement(node_instrucao, 'Parcelamentos')
            node_parcelamento = SubElement(node_parcelamentos, 'Parcelamento')
            minimo_parcela = SubElement(node_parcelamento, 'MinimoParcelas')
            minimo_parcela.text = parcela_minima
            maximo_parcela = SubElement(node_parcelamento, 'MaximoParcelas')
            maximo_parcela.text = parcela_maxima       

        # ----- URL de retorno para notificação ----- #
        # Se não for passada nenhuma será utilizada a que foi registrada na sua conta do moip
        if self.url_notificacao:
            node_url_notificacao = SubElement(node_instrucao, 'URLNotificacao')
            # url_notificacao.text = "{% url '{0}' %}".format(self.url_notificacao)
            node_url_notificacao.text = self.url_notificacao
        # ----- URL de retorno apos o pagamento ----- #
        node_url_retorno = SubElement(node_instrucao, 'URLRetorno')
        # url_retorno.text = "{% url '{0}' %}".format(self.url_retorno)
        node_url_retorno.text = self.url_retorno
        # ----- Converte para String ----- #
        xml = tostring(node_enviar_instrucao)
        
        return xml