# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 16:20:07 2021

@author: Daniel Souza - PC
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

print(str(Path(__file__).resolve().parents[1]))

from nota_corretagem import LoteNotaCorretagem


arquivo = '../arquivos/dani_02.pdf'

lote = LoteNotaCorretagem(arquivo)

print("Quantidade de Notas: {}".format(len(lote.notas)))

for nota in range(len(lote.notas)):
    print("++++++++++++++++++")
    print("++++++++++++++++++")
    print(f"NOTA {nota+1}")
    
    print(lote.notas[nota])