# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 18:29:04 2021

@author: Daniel Souza - PC
"""

import pdfquery

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from datetime import datetime
import math

import pandas as pd



class NotaCorretagem():
    # Define a constante EPSILON
    EPSILON_ = 0.5
    
    def __init__(self, arquivo = None):
        self.expressoes_ = {'data' : 'data pregão',
                           'nota' : ' nota',
                           'tabela_topo' : 'do título',
                           'tabela_fundo' : 'resumo financeiro',
                           'irrf' : 'i.r.p.f.',
                           'total' : 'íquido para'}
        self.data = None
        self.numero_nota = None
        self.transacoes = None
        self.transacoes_expandidas = None
        self.total_compras = 0
        self.total_vendas = 0
        self.irrf = 0
        self.total_liquido = 0
        self.total_taxas = 0
        
        if (arquivo != None):
            self.read_pdf(arquivo)

    
    
    ############################################################################
    def checa_nao_nulo_(self, item, **kwargs):
        try:
            extra = kwargs['extra']
        except KeyError:
            extra = ""
        if isinstance(item, str):
            return item != None and item.replace(' ', '') != "" and item != extra
        else:
            return item.text != None and item.text.replace(' ', '') != "" and item.text != extra

    ############################################################################
    def get_dist_(self, central, item):
        x1 = (float(central.get('x0')) + float(central.get('x1')))/2
        y1 = (float(central.get('y0')) + float(central.get('y1')))/2
        x2 = (float(item.get('x0')) + float(item.get('x1')))/2
        y2 = (float(item.get('y0')) + float(item.get('y1')))/2
        return math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )

    ############################################################################
    def padroniza_linha_(self, central, lista):
        resp = []
    
        for l in lista:        
            # Separa itens com espaço, caso eles sejam colacados no mesmo item
            resp = resp + l.text.split(' ')
        return [r for r in resp if self.checa_nao_nulo_(r, extra = '\n')]

    ############################################################################
    def ordena_reultados(self, item, lista, **kwargs):
        # Verifica se é ordenação reeversa
        try:
            reversa = kwargs['reversa']
        except KeyError:
            reversa = False
        # Retorna lista ordenada
        return sorted(lista, key=lambda x: self.get_dist_(item, x), reverse=reversa)

    ############################################################################
    def pdf_busca_item_texto_(self, texto, **kwargs):
        # Verifica se a busca precisa ser por texto identico
        try:
            identico = kwargs['identico']
        except KeyError:
            identico = False
        
        # Verifica a página da busca
        try:
            pg = kwargs['pg']
        except KeyError:
            pg = 1
        
        res = []
        res += self.pdf.pq('LTPage[pageid=\'{}\'] LTTextLineHorizontal:contains("{}")'.format(pg, texto)) 
        res += self.pdf.pq('LTPage[pageid=\'{}\'] LTTextBoxHorizontal:contains("{}")'.format(pg, texto)) 
    
        # Verifica se conteúdo é identico (espaços excluidos), caso aplicável
        if identico:
            res = [r for r in res if r.text.replace(' ', '') == texto.replace(' ', '')]
              
        return res
    
    ############################################################################
    def pdf_get_centro_item_(self, item):
        return ((float(item.get('x0')) + float(item.get('x1')))/2,
                (float(item.get('y0')) + float(item.get('y1')))/2)
    
    ############################################################################
    def pdf_busca_itens_linha_(self, item, **kwargs):
        
        
        # Define a sentido da busca, padrão 'horizontal'. Outras possibilidades 'direita', 'esquerda', 
        # 'vertical', 'acima', 'abaixo'
        try:
            sentido = kwargs['sentido']
        except KeyError:
            sentido = 'horizontal'
    
        # Define limite final da busca
        try:
            limites = kwargs['limites']
        except KeyError:
            if sentido in ['horizontal', 'direita', 'esquerda']:
                #TODO: Limites máximos a serem obtidos da pagina
                limites = (0, 595)
            else:
                limites = (0, 842)
                
        # Define página de busca
        try:
            pg = kwargs['pg']
        except KeyError:
            pg = 1
    
        # Define filtro de altura
        try:
            filtro = kwargs['filtro_altura']
            # Obtem parametros do filtro de altura
            altura_filtro = float(item.get('height'))
        except KeyError:
            filtro = False
    
        # Define filtro centralização
        try:
            centralizado = kwargs['centralizado']
            # Obtem parametros do filtro de altura
            ponto_central = self.pdf_get_centro_item_(item)
        except KeyError:
            centralizado = False
    
            
        ordenacao_reversa = False
        # Define a área de busca de acordo com extensao da busca
        if sentido == 'direita':
            # Coordenadas y são as do item, coordenadas x são o limite do item + epsilon e limites
            area_busca = (float(item.get('x1')) + self.EPSILON_, item.get('y0'), limites[1], item.get('y1'))
        elif sentido == 'esquerda':
            # Coordenadas y são as do item, coordenadas x são o limite do item + epsilon e limites
            area_busca = (limites[0], item.get('y0'), float(item.get('x0')) - self.EPSILON_, item.get('y1'))
            ordenacao_reversa = True
        elif sentido == 'abaixo':
            # Coordenadas x são as do item, coordenadas y são o limite do item + epsilon e limites
            area_busca = (item.get('x0'), limites[0], item.get('x1'), float(item.get('y0')) - self.EPSILON_)
        elif sentido == 'acima':
            # Coordenadas x são as do item, coordenadas y são o limite do item + epsilon e limites
            area_busca = (item.get('x0'), float(item.get('y1')) + self.EPSILON_, item.get('x1'), limites[1])
            ordenacao_reversa = True
            
        resultado = []
        # Vereifica se o sentido é 'horizontal' ou 'vertical', senão busca itens
        if sentido == 'horizontal':
            # Faz uma busca a esquerda e uma a direita
            resultado += self.pdf_busca_itens_linha_(item, sentido='esquerda', 
                                                     limites=limites, 
                                                     filtro_altura = filtro,
                                                     centralizado = centralizado, 
                                                     pg = pg)
            resultado += self.pdf_busca_itens_linha_(item, 
                                                     sentido='direita', 
                                                     limites=limites, 
                                                     filtro_altura = filtro,
                                                     centralizado = centralizado, 
                                                     pg = pg)
        elif sentido == 'vertical':
            # Faz uma busca acima e uma abaixo
            resultado += self.pdf_busca_itens_linha_(item, 
                                                     sentido='acima', 
                                                     limites=limites, 
                                                     filtro_altura = filtro,
                                                     centralizado = centralizado, 
                                                     pg = pg)
            resultado += self.pdf_busca_itens_linha_(item, sentido='abaixo', 
                                                     limites=limites, 
                                                     filtro_altura = filtro,
                                                     centralizado = centralizado, 
                                                     pg = pg)
        else:
            # Busca itens no arquivo
            busca = self.pdf.extract([('with_parent', 'LTPage[pageid=\'{}\']'.format(pg)), 
                                 ('res', ':overlaps_bbox("%s, %s, %s, %s")' % area_busca)])
            # Retira itens nulos e em branco
            res_busca = [r for r in busca['res'] if self.checa_nao_nulo_(r)]
            # Filtra itens por altura, caso passe de 30% de discrepância da altura
            if filtro:
                res_busca = [r for r in res_busca if float(r.get('height')) >= 0.7*altura_filtro and \
                             float(r.get('height')) <= 1.3*altura_filtro]
            
            # Filtra itens centralizados, caso aplicável
            if centralizado:
                if sentido in ['direita', 'esquerda']:
                    # Verifica se a coordena y está dentro da tolerância
                    res_busca = [r for r in res_busca if abs(self.pdf_get_centro_item_(r)[1] - ponto_central[1]) < 2*self.EPSILON_]
                elif sentido in ['acima', 'abaixo']:
                    # Verifica se a coordena x está dentro da tolerância
                    res_busca = [r for r in res_busca if abs(self.pdf_get_centro_item_(r)[0] - ponto_central[0]) < 2*self.EPSILON_]
            # Ordena resultados
            resultado = self.ordena_reultados(item, res_busca, reversa = ordenacao_reversa)
    
        return resultado
        
    ############################################################################
    def pdf_view_boxes(self, boxes):
    
        # Create figure and axes
        plt.figure()
        ax = plt.gca()
    
        if boxes == None:
            # Varre todos objetos de texto
            texts = self.pdf.pq('LTPage[pageid=\'1\'] LTTextLineHorizontal') +\
                self.pdf.pq('LTPage[pageid=\'1\'] LTTextBoxHorizontal')
                
            for t in texts:
                x = float(t.get('x0'))
                y = float(t.get('y0'))
                x1 = float(t.get('x1'))
                y1 = float(t.get('y1'))
    
                rect = Rectangle((x, y), x1-x, y1-y, linewidth=1, edgecolor='r', facecolor='none')
                ax.add_patch(rect)
    
            boxes = self.pdf.pq('LTPage[pageid=\'1\'] LTRect') + \
                self.pdf.pq('LTPage[pageid=\'1\'] LTCurve') + \
                self.pdf.pq('LTPage[pageid=\'1\'] LTImage') + \
                self.pdf.pq('LTPage[pageid=\'1\'] LTLine')
                
            for t in boxes:
                x = float(t.get('x0'))
                y = float(t.get('y0'))
                x1 = float(t.get('x1'))
                y1 = float(t.get('y1'))
    
                rect = Rectangle((x, y), x1-x, y1-y, linewidth=1, edgecolor='b',
                                 facecolor='none', hatch='-')
                ax.add_patch(rect)
        else:
            for t in boxes:
                x = float(t.get('x0'))
                y = float(t.get('y0'))
                x1 = float(t.get('x1'))
                y1 = float(t.get('y1'))
    
                rect = Rectangle((x, y), x1-x, y1-y, linewidth=1, edgecolor='k', facecolor='none')
                ax.add_patch(rect)
    
    
        # Add collection to axes
        #ax.add_collection(pc)
        ax.set_xlim([0, 600])
        ax.set_ylim([0, 850])
        plt.show()
    
    ############################################################################
    def limpa_chars_(self, texto):
        texto = texto.replace(' ', '').replace('\n','')
        return texto.replace('.', '').replace(',', '.')
    
    ############################################################################
    def pdf_get_cabecalho_(self):
        
        # Data da operação
        element = self.pdf_busca_itens_linha_(
            self.pdf_busca_item_texto_(self.expressoes_['data'])[0], 
            sentido = 'abaixo')[0]
        data = datetime.strptime(self.limpa_chars_(element.text), "%d/%m/%Y").date()
        
        self.data = data
            
        # Número da nota
        element = self.pdf_busca_itens_linha_(
            self.pdf_busca_item_texto_(self.expressoes_['nota'])[0], 
            sentido = 'abaixo')[0]
        nota = int(self.limpa_chars_(element.text))
        
        self.numero_nota = nota
        
        
        # Dados da última página
        page = self.pdf_paginas_
                
        # Busca as taxa de IRRF
        try:
            element = self.pdf_busca_itens_linha_(
                self.pdf_busca_item_texto_(self.expressoes_['irrf'], pg = page)[0],
                sentido = 'direita', 
                filtro_altura = True, 
                centralizado = True, 
                pg = page)[0]
            tx_irrf = abs(float(self.limpa_chars_(element.text)))
        except IndexError:
            # Caso não conste na nota este campo (Modal)
            tx_irrf = 0.0
        self.irrf = tx_irrf
         
        # Busca Total líquido
        element = self.pdf_busca_itens_linha_(
            self.pdf_busca_item_texto_(self.expressoes_['total'], pg = page)[0],
            sentido = 'direita', 
            filtro_altura = True, 
            centralizado = True, 
            pg = page)[0]
        total = abs(float(self.limpa_chars_(element.text)))
        
        self.total_liquido = total            
            
    ############################################################################
    def pdf_get_transacoes(self):
        transacoes = []
        
        # Varre as páginas
        for page in range(1,self.pdf_paginas_+1):
    
            # Busca inicio da tabela
            tabela_inicio = self.pdf_busca_item_texto_(self.expressoes_['tabela_topo'], pg = page)[0]
            # Busca inicio da tabela
            tabela_fim = self.pdf_busca_item_texto_(self.expressoes_['tabela_fundo'], pg = page)[0]
        
            # Define os limites da busca (abaixo de 'do Titulo' e acima de 'RESUMO')
            limites_busca = (float(tabela_fim.get('y1')) + 0.5, 0) #TODO: trocar por EPSILON
        
            # Busca itens abaixo do local escrito 'do Título'
            resultados = self.pdf_busca_itens_linha_(tabela_inicio, 
                                                    sentido = 'abaixo', 
                                                    limites = limites_busca, 
                                                    pg = page)
            
            for resultado in resultados:
                linha = {}
                
                # Obtem somente o nome do ativo
                atv = resultado.text.replace('\n','').upper()
                atv = ' '.join(atv.split())
                linha['ativo'] = atv
        
                # Busca todos itens não nulos na mesma linha, a esquerda e a direita dele
                res = self.pdf_busca_itens_linha_(resultado, 
                                                  sentido = 'horizontal', 
                                                  filtro_altura = True, 
                                                  pg = page)
                linha_lista = self.padroniza_linha_(resultado, res)
        
                # Obtem tipo da transação (Compra ou venda)
                tipo = 'Venda'
                sinal = -1
                if linha_lista[1] == 'c':
                    tipo = 'Compra'
                    sinal = 1
                    
                linha['operacao'] = tipo

                # Obtem quantidade de ativos negociados
                qtd = int(linha_lista[-4].replace('.', ''))
                linha['quantidade'] = qtd
                
                # Obtem preço da transação
                preco = float(linha_lista[-3].replace(',', '.'))
                linha['preco'] = preco
                
                # Calcula valor da transação (sinal negativo para venda)
                linha['valor'] = preco * sinal * qtd
                    
                transacoes.append(linha)
            
                    
        # Cria dataframe das transações
        self.transacoes_expandidas = pd.DataFrame(transacoes)
        
        # Consolida transações por ativo e tipo de operação
        self.transacoes = self.transacoes_expandidas.groupby(['ativo', 'operacao']).sum()[['quantidade','valor']]
        self.transacoes['preco'] = abs(self.transacoes['valor']) / self.transacoes['quantidade']
        

    ############################################################################
    def pdf_processa_nota(self):
        
        self.pdf_get_cabecalho_()
        
        self.pdf_get_transacoes()
        
        # Calcula dados faltantes
        # Total de compras
        self.total_compras = self.transacoes_expandidas.loc[
            self.transacoes_expandidas.operacao == "Compra", 'valor'].sum()
        
        # Total de vendas
        self.total_vendas = abs(self.transacoes_expandidas.loc[
            self.transacoes_expandidas.operacao == "Venda", 'valor'].sum())
        
        # Total de taxas
        self.total_taxas = abs(abs(self.total_compras - self.total_vendas) \
                               - self.total_liquido)
        
        
        tot_operacoes = self.total_compras + self.total_vendas
        
        self.transacoes['taxas'] = abs(self.transacoes['valor'])/tot_operacoes * self.total_taxas
        
        self.transacoes['valor_liquido'] = self.transacoes['valor'] + self.transacoes['taxas']
        
        
    ############################################################################
    def __str__(self):
        string = 'Data: ' + self.data.isoformat() + '\n'
        string += 'Nota de corretagem: {}'.format(self.numero_nota) + '\n'
        
        string += '------------------------------\n'
        string += '- Transações \n'
        string += '------------------------------\n'
        
        string += str(self.transacoes) + '\n'
        
        string += '------------------------------\n'
        
        string += "Total de compras: R${:.2f}".format(self.total_compras) + '\n'
        string += "Total de vendas: R${:.2f}".format(self.total_vendas) + '\n'
        string += "Total de taxas: R${:.2f}".format(self.total_taxas) + '\n'
        string += "Taxa de I.R.R.F.: R${:.2f}".format(self.irrf) + '\n'
        
        string += '------------------------------\n'
        string += "Total Líquido: R${:.2f}".format(self.total_liquido) + '\n'
        
        return string
    ############################################################################
    def read_pdf(self, arquivo):
        try:
            with open(arquivo, 'rb') as file:
                self.pdf = pdfquery.PDFQuery(file,
                                        input_text_formatter= lambda x: x.lower())
                self.pdf.load()
                
                # uncomment the two lines below to write the xml
                # of the PDF to a file, helps to find coordinates of data
                
                #with open('xmltree.xml','wb') as f:
                #     f.write(etree.tostring(pdf.tree, pretty_print=True))
                #printBboxes(None)

                self.pdf_paginas_ = len(self.pdf._pages)
                
                # Processa Nota
                self.dados_nota = self.pdf_processa_nota()
                

            
        except FileNotFoundError:
            print("Error while openning the file.")
            # TODO: raise exception or return error?






        

