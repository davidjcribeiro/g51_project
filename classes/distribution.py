# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 00:31:27 2026

@author: Martim
"""

from classes.Gclass import Gclass

class Distribution(Gclass):
    obj = {}
    lst = []
    pos = -1
    sortkey = ''
    att = ['_id', '_plant_id', '_grid_id', '_date', '_energy_kwh']
    headers = 'Plano de Distribuição'
    des = ['ID Distribuição', 'ID Central', 'ID Rede', 'Data', 'Energia (kWh)']

    def __init__(self, id=0, plant_id=0, grid_id=0, date="", energy_kwh=0.0):
        super().__init__()
        self._id = Distribution.get_id(id)
        self._plant_id = plant_id
        self._grid_id = grid_id
        self._date = date
        self._energy_kwh = float(energy_kwh)
       
        Distribution.obj[self._id] = self
        Distribution.lst.append(self._id)

    @property
    def id(self): return self._id

    @property
    def plant_id(self): return self._plant_id
    @plant_id.setter
    def plant_id(self, value): self._plant_id = value

    @property
    def grid_id(self): return self._grid_id
    @grid_id.setter
    def grid_id(self, value): self._grid_id = value

    @property
    def date(self): return self._date
    @date.setter
    def date(self, value): self._date = value

    @property
    def energy_kwh(self): return self._energy_kwh
    @energy_kwh.setter
    def energy_kwh(self, value): self._energy_kwh = value
    
