# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 00:31:22 2026

@author: Martim
"""

from classes.Gclass import Gclass

class Grid(Gclass):
    obj = {}
    lst = []
    pos = -1
    sortkey = ''
    att = ['_id', '_name', '_address']
    headers = 'Redes de Distribuição'
    des = ['ID Rede', 'Nome da Rede', 'Morada/Setor']

    def __init__(self, id=0, name="", address=""):
        super().__init__()
        self._id = Grid.get_id(id)
        self._name = name
        self._address = address
       
        Grid.obj[self._id] = self
        Grid.lst.append(self._id)

    @property
    def id(self): return self._id

    @property
    def name(self): return self._name
    @name.setter
    def name(self, value): self._name = value

    @property
    def address(self): return self._address
    @address.setter
    def address(self, value): self._address = value


