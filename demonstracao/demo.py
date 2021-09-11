# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 16:20:07 2021

@author: Daniel Souza - PC
"""
import sys
from pathlib import Path
sys.path.append(str(Path('.').absolute().parent))

from nota_corretagem import NotaCorretagem


arquivo = '../arquivos/nota_exemplo.pdf'

nota = NotaCorretagem(arquivo)

print(nota)

print("Transações Completas:")
print(nota.transacoes_expandidas)