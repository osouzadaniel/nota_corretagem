# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 18:29:04 2021

@author: Daniel Souza - PC
"""
arquivo = 'arquivos/nota_exemplo3.pdf'




import pdfquery
from lxml import etree

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from datetime import datetime
import math

import pandas as pd



class NotaCorretagem():
    # Define a constante EPSILON
    EPSILON_ = 0.5
    
    def __init__(self):
        self.expressoes_ = {'data' : 'data pregão',
                           'nota' : ' nota',
                           'tabela_topo' : 'do título',
                           'tabela_fundo' : 'resumo financeiro',
                           'liquidacao' : 'taxa de liquidação',
                           'registro' : 'taxa de registro',
                           'termo' : 'taxa de termo',
                           'ana' : 'a.n.a.',
                           'emolumentos' : 'emolumentos',
                           'corretagem' : 'taxa operacional',
                           'corretagem_identico' : False,
                           'iss' : 'iss',
                           'irrf' : 'i.r.p.f.',
                           'outras' : 'outros',
                           'total' : 'íquido para'}
        self.data = None

    
    
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
    def pdf_processa_nota(self, to_print = False):
        
        # Dados a serem retornados
        dados_gerais = {}
        tabela = []
        
        
        # Data da operação
        #element = pdf.pq('LTPage[pageid=\'1\'] LTTextLineHorizontal:contains("Data")')[0]
        element = self.pdf_busca_itens_linha_(
            self.pdf_busca_item_texto_(self.expressoes_['data'])[0], 
            sentido = 'abaixo')[0]
        data = datetime.strptime(element.text.replace(' ', '').replace('\n',''), "%d/%m/%Y").date()
        
        dados_gerais['data'] = data
        if to_print:
            print('Data: ' + data.isoformat())
        # Númerod a nota
        element = self.pdf_busca_itens_linha_(
            self.pdf_busca_item_texto_(self.expressoes_['nota'])[0], 
            sentido = 'abaixo')[0]
        nota = int(element.text.replace(' ', ''))
        
        dados_gerais['numero_nota'] = nota
        if to_print:
            print('Nota de corretagem: {}'.format(nota))
        
        for page in range(1,self.pdf_paginas_+1):
            if to_print:
                print("+++ PÁGINA {} +++".format(page))
    
            # Busca inicio da tabela
            tabela_inicio = self.pdf_busca_item_texto_(self.expressoes_['tabela_topo'], pg = page)[0]
            # Busca inicio da tabela
            tabela_fim = self.pdf_busca_item_texto_(self.expressoes_['tabela_fundo'], pg = page)[0]
        
            # Define os limites da busca (abaixo de 'do Titulo' e acima de 'RESUMO')
            limites_busca = (float(tabela_fim.get('y1')) + 0.5, 0) #TODO: trocar por EPSILON
        
            # Busca itens abaixo do local escrito 'do Título'
            resultado = self.pdf_busca_itens_linha_(tabela_inicio, 
                                                    sentido = 'abaixo', 
                                                    limites = limites_busca, 
                                                    pg = page)
        
            for c in resultado:
                linha = {}
                
                # Obtem somente o nome do ativo
                atv = c.text.replace('\n','').upper()
                linha['ativo'] = atv
                if to_print:
                    print('-------------')
                    print(atv)
        
                # Busca todos itens não nulos na mesma linha, a esquerda e a direita dele
                res = self.pdf_busca_itens_linha_(c, 
                                                  sentido = 'horizontal', 
                                                  filtro_altura = True, 
                                                  pg = page)
                lin = self.padroniza_linha_(c, res)
        
                # Obtem os dados
                tipo = 'Venda'
                sinal = -1
                if lin[1] == 'c':
                    tipo = 'Compra'
                    sinal = 1
                linha['operacao'] = tipo
                if to_print:
                    print(tipo)
        
                qtd = int(lin[-4].replace('.', ''))
                linha['quantidade'] = qtd
                if to_print:
                    print('Quantidade: {}'.format(qtd))
        
                preco = float(lin[-3].replace(',', '.'))
                linha['preco'] = preco * sinal
                if to_print:
                    print('Preço: R${}'.format(preco))
        
                if to_print:
                    print('Total: R${}'.format(preco*qtd))
                    
                tabela.append(linha)
            
            if page == self.pdf_paginas_:
                """
                if to_print:
                    print('+-+-+-+-+-+-+-+-+-+-+-+-+')
                # Busca as taxa de liquidação
                element = buscaItensEmLinha(buscaItemTexto(expressoes[corretora]['liquidacao'], pg = page)[0],
                                            sentido = 'direita', filtro_altura = True, centralizado = True, pg = page)[0]
                tx_liquidacao = abs(float(element.text.replace(' ', '').replace(',', '.')))
                if to_print:
                    print("Taxa de liquidação: R${}".format(tx_liquidacao))
            
                # Busca as taxa de registro
                element = buscaItensEmLinha(buscaItemTexto(expressoes[corretora]['registro'], pg = page)[0],
                                            sentido = 'direita', filtro_altura = True, centralizado = True, pg = page)[0]
                tx_registro = abs(float(element.text.replace(' ', '').replace(',', '.')))
                if to_print:
                    print("Taxa de registro: R${}".format(tx_registro))
            
                # Busca as taxa de termo
                element = buscaItensEmLinha(buscaItemTexto(expressoes[corretora]['termo'], pg = page)[0],
                                            sentido = 'direita', filtro_altura = True, centralizado = True, pg = page)[0]
                tx_termo = abs(float(element.text.replace(' ', '').replace(',', '.')))
                if to_print:
                    print("Taxa de termo: R${}".format(tx_termo))
            
                # Busca as taxa de ana
                element = buscaItensEmLinha(buscaItemTexto(expressoes[corretora]['ana'], pg = page)[0],
                                            sentido = 'direita', filtro_altura = True, centralizado = True, pg = page)[0]
                tx_ana = abs(float(element.text.replace(' ', '').replace(',', '.')))
                if to_print:
                    print("Taxa de A.N.A.: R${}".format(tx_ana))
            
                # Busca as taxa de emolumentos
                element = buscaItensEmLinha(buscaItemTexto(expressoes[corretora]['emolumentos'], pg = page)[0],
                                            sentido = 'direita', filtro_altura = True, centralizado = True, pg = page)[0]
                tx_emolumentos = abs(float(element.text.replace(' ', '').replace(',', '.')))
                if to_print:
                    print("Taxa de emolumentos: R${}".format(tx_emolumentos))
            
                # Busca as taxa de corretagem
                element = buscaItensEmLinha(buscaItemTexto(expressoes[corretora]['corretagem'],
                                                           identico = expressoes[corretora]['corretagem_identico'], pg = page)[0],
                                            sentido = 'direita', filtro_altura = True, centralizado = True, pg = page)[0]
                tx_corretagem = abs(float(element.text.replace(' ', '').replace(',', '.')))
                if to_print:
                    print("Taxa de corretagem: R${}".format(tx_corretagem))
                
                
                # Busca as taxa de ISS
                element = buscaItensEmLinha(buscaItemTexto(expressoes[corretora]['iss'], pg = page)[0],
                                            sentido = 'direita', filtro_altura = True, centralizado = True, pg = page)[0]
                tx_iss = abs(float(element.text.replace(' ', '').replace(',', '.')))
                if to_print:
                    print("Taxa de ISS: R${}".format(tx_iss))
                    
                # Busca as taxa de Outras
                element = buscaItensEmLinha(buscaItemTexto(expressoes[corretora]['outras'], pg = page)[0],
                                            sentido = 'direita', filtro_altura = True, centralizado = True, pg = page)[0]
                tx_outras = abs(float(element.text.replace(' ', '').replace(',', '.')))
                if to_print:
                    print("Outras taxas: R${}".format(tx_outras))
                """
                # Busca as taxa de IRRF
                try:
                    element = self.pdf_busca_itens_linha_(
                        self.pdf_busca_item_texto_(self.expressoes_['irrf'], pg = page)[0],
                        sentido = 'direita', 
                        filtro_altura = True, 
                        centralizado = True, 
                        pg = page)[0]
                    tx_irrf = abs(float(element.text.replace(' ', '').replace(',', '.')))
                except IndexError:
                    # Caso não conste na nota este campo (Modal)
                    tx_irrf = 0.0
                dados_gerais['irrf'] = tx_irrf
                if to_print:
                    print("Taxa de I.R.R.F.: R${}".format(tx_irrf))
            
                
                    
                # Busca Total líquido
                element = self.pdf_busca_itens_linha_(
                    self.pdf_busca_item_texto_(self.expressoes_['total'], pg = page)[0],
                    sentido = 'direita', 
                    filtro_altura = True, 
                    centralizado = True, 
                    pg = page)[0]
                total = abs(float(element.text.replace(' ', '').replace('.', '').replace(',', '.').replace('\n','')))
                dados_gerais['total_liquido'] = total
                if to_print:
                    print("Total Líquido: R${}".format(total))
                
                    
        # Cria dataframe da tabela
        df= pd.DataFrame(tabela)
        df['valor'] = df['preco'] * df['quantidade']
        dados_gerais['transacoes'] = df
        
        return dados_gerais
    ############################################################################
    
    def read_pdf(self, file):
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
                
                # Identifica a corretora
                self.dados_nota = self.pdf_processa_nota(to_print = False)
                self.df = self.dados_nota['transacoes'].groupby(['ativo', 'operacao']).sum()[['quantidade','valor']]
                self.df['preco'] = abs(self.df['valor']) / self.df['quantidade']

            
        except FileNotFoundError:
            print("Error while openning the file.")
            # TODO: raise exception or return error?

nota = NotaCorretagem()
nota.read_pdf(arquivo)

"""   
    if not suporte:
        print("Nota de corretagem não suportada!")
    else:
        print("Nota lida com sucesso!")
        lista = dados_nota['transacoes']
        tot_compra = lista.loc[lista.operacao == "Compra", 'valor'].sum()
        print("Total de compras: R${:.2f}".format(tot_compra))
        
        tot_venda = abs(lista.loc[lista.operacao == "Venda", 'valor'].sum())
        print("Total de vendas: R${:.2f}".format(tot_venda))
        
        print("Total líquido: R${:.2f}".format(dados_nota['total_liquido']))
        
        taxas = abs(abs(tot_compra - tot_venda) - dados_nota['total_liquido'])
        print("Total de taxas: R${:.2f}".format(taxas))
        
        tot_operacoes = tot_compra + tot_venda
        
        df['taxa'] = abs(df['valor'])/tot_operacoes * taxas
        
        df['valor_liquido'] = df['valor'] + df['taxa']
        #df.iloc[df.index.get_locs([slice(None), ['Venda']]), -1] = df.iloc[df.index.get_locs([slice(None), ['Venda']])]['valor'] \
        #    - df.iloc[df.index.get_locs([slice(None), ['Venda']])]['taxa']
        #df2.loc['valor_liquido'] = df2['valor'] - df2['taxa']
        
"""   
        

