# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 16:20:07 2021

@author: Daniel Souza - PC
"""
import sys
from pathlib import Path
path_root = Path(__file__).resolve().parents[1]
sys.path.append(str(path_root))

from nota_corretagem import LoteNotaCorretagem

if len(sys.argv) > 1:
    fname = sys.argv[1]
else:
    fname = 'nota_itau2.pdf'

arquivo = (path_root / 'arquivos' / fname).resolve()

lote = LoteNotaCorretagem(arquivo)

print("Quantidade de Notas: {}".format(len(lote.notas)))

for nota in range(len(lote.notas)):
    print("++++++++++++++++++")
    print("++++++++++++++++++")
    print(f"NOTA {nota+1}")
    
    print(lote.notas[nota])
