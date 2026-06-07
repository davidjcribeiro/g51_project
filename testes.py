# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 17:03:10 2026

@author: Martim
"""

from classes.Gclass import Gclass
from classes.grid import Grid
from classes.distribution import Distribution
from classes.company import Company
from classes.plant import Plant

if __name__ == '__main__':
    print("Início dos Testes: Classe Company\n")

    print("1.Instâncias:")
    try:
        comp1 = Company(id=1, name="Lusa Energia", creation_date="1995-10-15")
        comp2 = Company(id=2, name="Solaris PT", creation_date="2012-04-20")
        print(f"Foram criadas as empresas com IDs: {comp1.id} e {comp2.id}\n")
    except Exception as e:
        print(f"Erro ao criar instâncias: {e}\n")

    print("2.Getters:")
    print(f"Detalhes da Empresa 1:")
    print(f" - ID da Empresa:   {comp1.id}")
    print(f" - Nome:            {comp1.name}")
    print(f" - Data de Criação: {comp1.creation_date} \n")

    print("3.Setters:")
    print("A alterar o nome da Empresa 1 para 'Lusa Energia Renovável' e a data para '1995-12-01'...")
    comp1.name = "Lusa Energia Renovável"
    comp1.creation_date = "1995-12-01"

    if comp1.name == "Lusa Energia Renovável" and comp1.creation_date == "1995-12-01":
        print(f"Novos valores -> Nome: {comp1.name}, Data de Criação: {comp1.creation_date}\n")
    else:
        print("Os Setters não atualizaram os valores corretamente.\n")

    print("4. Armazenamento:")
    print(f"Lista de IDs armazenados (Company.lst): {Company.lst}")
    
    print("Objetos no dicionário (Company.obj):")
    for obj_id, obj_instance in Company.obj.items():
        print(f" - Chave: {obj_id} | Valor: Objeto Company (Nome: {obj_instance.name}, Data de Criação: {obj_instance.creation_date})")

    if len(Company.lst) == len(Company.obj):
        print("O dicionário e a lista estão sincronizados.\n")
    else:
        print("Aviso: O número de elementos em 'lst' e 'obj' não coincide.\n")

print("-----------------------------------------------------------------------------------------\n")  

if __name__ == '__main__':
    print("Início dos Testes: Classe Plant\n")

    print("1.Instâncias:")
    try:
        plant1 = Plant(id=1, comments="Central Solar Fotovoltaica - Alentejo", company_id=10)
        plant2 = Plant(id=2, comments="Parque Eólico offshore", company_id=15)
        print(f"Foram criadas as centrais com IDs: {plant1.id} e {plant2.id}\n")
    except Exception as e:
        print(f"Erro ao criar instâncias: {e}\n")

    # 2. Testar Getters (Leitura de propriedades)
    print("2.Getters:")
    print(f"Detalhes da Central 1:")
    print(f" - ID da Central: {plant1.id}")
    print(f" - Comentários:   {plant1.comments}")
    print(f" - ID Empresa:    {plant1.company_id}  \n")

    print("3.Setters:")
    print("A alterar os comentários da Central 1 e a atribuir um novo ID de empresa (20)...")
    plant1.comments = "Central Solar Fotovoltaica - Alentejo (Em expansão)"
    plant1.company_id = 20

    if plant1.comments == "Central Solar Fotovoltaica - Alentejo (Em expansão)" and plant1.company_id == 20:
        print(f"Novos valores -> Comentários: {plant1.comments}, ID Empresa: {plant1.company_id}\n")
    else:
        print("Os Setters não atualizaram os valores corretamente.\n")

    print("4.Armazenamento:")
    print(f"Lista de IDs armazenados (Plant.lst): {Plant.lst}")
    
    print("Objetos no dicionário (Plant.obj):")
    for obj_id, obj_instance in Plant.obj.items():
        print(f" - Chave: {obj_id} | Valor: Objeto Plant (Empresa: {obj_instance.company_id}, Comentários: '{obj_instance.comments}')")

    if len(Plant.lst) == len(Plant.obj):
        print("O dicionário e a lista estão sincronizados.\n")
    else:
        print("Aviso: O número de elementos em 'lst' e 'obj' não coincide.\n")


print("-----------------------------------------------------------------------------------------\n")  

if __name__ == '__main__':
    print("Início dos Testes: Classe Distribution \n")

    print("1.Instâncias:")
    try:
        dist1 = Distribution(id=1, plant_id=101, grid_id=201, date="2026-04-26", energy_kwh=500.5)
        dist2 = Distribution(id=2, plant_id=102, grid_id=202, date="2026-04-27", energy_kwh=750.0)
        print(f"Foram criadas as distribuições com IDs: {dist1.id} e {dist2.id}\n")
    except Exception as e:
        print(f"Erro ao criar instâncias: {e}\n")

    print("2.Getters:")
    print("Detalhes da Distribuição 1:")
    print(f" - Central ID: {dist1.plant_id}")
    print(f" - Rede ID:    {dist1.grid_id}")
    print(f" - Data:       {dist1.date}")
    print(f" - Energia:    {dist1.energy_kwh} kWh \n")

    print("3.Setters:")
    print("A alterar a energia da Distribuição 1 para 600.0 e a data para '2026-05-01'...")
    dist1.energy_kwh = 600.0
    dist1.date = "2026-05-01"

    if dist1.energy_kwh == 600.0 and dist1.date == "2026-05-01":
        print(f"Novos valores -> Data: {dist1.date}, Energia: {dist1.energy_kwh} kWh\n")
    else:
        print("Os Setters não atualizaram os valores corretamente.\n")

    print("4.Armazenamento:")
    print(f"Lista de IDs armazenados (Distribution.lst): {Distribution.lst}")
    
    print("Objetos no dicionário (Distribution.obj):")
    for obj_id, obj_instance in Distribution.obj.items():
        print(f" - Chave: {obj_id} | Valor: Objeto Distribution (Central: {obj_instance.plant_id}, Energia: {obj_instance.energy_kwh})")

    if len(Distribution.lst) == len(Distribution.obj):
        print("O dicionário e a lista estão sincronizados.\n")
    else:
        print("O número de elementos em 'lst' e 'obj' não coincide.\n")
        
print("-----------------------------------------------------------------------------------------\n")        
        
if __name__ == '__main__':
    print("Início dos Testes: Classe Grid \n")

    print("1.Instâncias:")
    try:
        grid1 = Grid(id=1, name="Rede Norte", address="Zona Industrial, Lote 4")
        grid2 = Grid(id=2, name="Rede Sul", address="Avenida Central, Setor B")
        print(f"Foram criadas as redes com IDs: {grid1.id} e {grid2.id}\n")
    except Exception as e:
        print(f"Erro ao criar instâncias: {e}\n")

    print("2.Getters:")
    print("Detalhes da Rede 1:")
    print(f" - ID da Rede: {grid1.id}")
    print(f" - Nome:       {grid1.name}")
    print(f" - Morada:     {grid1.address}\n")

    print("3.Setters:")
    print("A alterar o nome da Rede 1 para 'Rede Nordeste' e a morada para 'Parque Tecnológico'...")
    grid1.name = "Rede Nordeste"
    grid1.address = "Parque Tecnológico"

    if grid1.name == "Rede Nordeste" and grid1.address == "Parque Tecnológico":
        print(f"Novos valores -> Nome: {grid1.name}, Morada: {grid1.address}\n")
    else:
        print("Os Setters não atualizaram os valores corretamente.\n")

    print("4.Armazenamento:")
    print(f"Lista de IDs armazenados (Grid.lst): {Grid.lst}")
    
    print("Objetos no dicionário (Grid.obj):")
    for obj_id, obj_instance in Grid.obj.items():
        print(f" - Chave: {obj_id} | Valor: Objeto Grid (Nome: {obj_instance.name}, Morada: {obj_instance.address})")

    if len(Grid.lst) == len(Grid.obj):
        print("O dicionário e a lista estão sincronizados.\n")
    else:
        print("O número de elementos em 'lst' e 'obj' não coincide.\n")