"""
Script para popular a base de dados TrabalhoPCII.db com dados realistas
de distribuição de energia em Portugal.
"""
import sqlite3
import random
from datetime import datetime, timedelta

random.seed(42)

conn = sqlite3.connect('data/TrabalhoPCII.db')
cursor = conn.cursor()

# --- Limpar tabelas existentes ---
for table in ['Distribution', 'Plant', 'Grid', 'Company']:
    cursor.execute(f"DELETE FROM {table}")

# --- Empresas de Energia ---
companies = [
    (1, "2001-06-15", "EDP Renováveis"),
    (2, "2010-03-22", "Galp Energia"),
    (3, "1998-11-08", "Endesa Portugal"),
    (4, "2015-07-01", "Iberwind"),
    (5, "2005-09-30", "Luso Energia"),
    (6, "2018-01-12", "Solaris PT"),
    (7, "2012-05-20", "Greenvolt"),
    (8, "2020-02-14", "Voltalia Portugal"),
]

for c in companies:
    cursor.execute("INSERT INTO Company (company_id, company_creation_date, company_name) VALUES (?, ?, ?)", c)

# --- Redes de Distribuição ---
grids = [
    (1, "Rede Norte", "Porto, Zona Industrial"),
    (2, "Rede Centro", "Coimbra, Parque Tecnológico"),
    (3, "Rede Sul", "Faro, Setor Comercial"),
    (4, "Rede Lisboa", "Lisboa, Centro Empresarial"),
    (5, "Rede Alentejo", "Évora, Zona Rural"),
    (6, "Rede Minho", "Braga, Distrito Industrial"),
    (7, "Rede Trás-os-Montes", "Vila Real, Serra"),
    (8, "Rede Algarve", "Portimão, Zona Costeira"),
    (9, "Rede Ribatejo", "Santarém, Vale do Tejo"),
    (10, "Rede Beira Interior", "Guarda, Zona Montanhosa"),
]

for g in grids:
    cursor.execute("INSERT INTO Grid (grid_id, grid_name, grid_address) VALUES (?, ?, ?)", g)

# --- Centrais de Produção ---
plants = [
    (1, 1, "Central Solar Fotovoltaica - Alentejo"),
    (2, 1, "Parque Eólico - Serra da Estrela"),
    (3, 2, "Central de Biomassa - Leiria"),
    (4, 2, "Parque Solar - Algarve"),
    (5, 3, "Central Hidroelétrica - Douro"),
    (6, 3, "Parque Eólico - Trás-os-Montes"),
    (7, 4, "Parque Eólico Offshore - Viana do Castelo"),
    (8, 5, "Central Solar Concentrada - Beja"),
    (9, 6, "Minicentral Hidroelétrica - Minho"),
    (10, 6, "Parque Fotovoltaico - Setúbal"),
    (11, 7, "Central de Biomassa - Viseu"),
    (12, 7, "Parque Eólico - Peniche"),
    (13, 8, "Central Solar Flutuante - Alqueva"),
    (14, 8, "Parque Fotovoltaico - Moura"),
    (15, 4, "Central Eólica Terrestre - Abrantes"),
]

for p in plants:
    cursor.execute("INSERT INTO Plant (plant_id, company_id, plant_comments) VALUES (?, ?, ?)", p)

# --- Distribuições (dados de 2023-2026) ---
start_date = datetime(2023, 1, 1)
end_date = datetime(2026, 5, 1)

# Definir padrões sazonais (fator multiplicador por mês)
# Inverno: mais eólica/hidro, Verão: mais solar
seasonal_solar = {1: 0.4, 2: 0.5, 3: 0.7, 4: 0.85, 5: 1.0, 6: 1.3, 7: 1.4, 8: 1.35, 9: 1.1, 10: 0.8, 11: 0.5, 12: 0.35}
seasonal_wind = {1: 1.3, 2: 1.2, 3: 1.1, 4: 0.9, 5: 0.8, 6: 0.6, 7: 0.5, 8: 0.55, 9: 0.7, 10: 1.0, 11: 1.2, 12: 1.35}
seasonal_hydro = {1: 1.4, 2: 1.3, 3: 1.2, 4: 1.0, 5: 0.85, 6: 0.5, 7: 0.3, 8: 0.25, 9: 0.4, 10: 0.7, 11: 1.1, 12: 1.3}
seasonal_bio = {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0, 7: 1.0, 8: 0.9, 9: 1.0, 10: 1.0, 11: 1.0, 12: 1.0}

# Tipo de central e energia base (kWh/dia)
plant_types = {
    1: ("solar", 12000),    # Central Solar Fotovoltaica
    2: ("wind", 18000),     # Parque Eólico
    3: ("bio", 8000),       # Central de Biomassa
    4: ("solar", 10000),    # Parque Solar
    5: ("hydro", 25000),    # Central Hidroelétrica
    6: ("wind", 15000),     # Parque Eólico
    7: ("wind", 22000),     # Parque Eólico Offshore
    8: ("solar", 14000),    # Central Solar Concentrada
    9: ("hydro", 6000),     # Minicentral Hidroelétrica
    10: ("solar", 11000),   # Parque Fotovoltaico
    11: ("bio", 7000),      # Central de Biomassa
    12: ("wind", 16000),    # Parque Eólico
    13: ("solar", 9000),    # Central Solar Flutuante
    14: ("solar", 13000),   # Parque Fotovoltaico
    15: ("wind", 12000),    # Central Eólica Terrestre
}

seasonal_map = {"solar": seasonal_solar, "wind": seasonal_wind, "hydro": seasonal_hydro, "bio": seasonal_bio}

# Associar centrais a redes (cada central distribui para 2-4 redes)
plant_grid_map = {
    1: [3, 5],
    2: [2, 10],
    3: [2, 9],
    4: [3, 8],
    5: [1, 6, 7],
    6: [7, 10],
    7: [1, 6],
    8: [5, 3],
    9: [6, 1],
    10: [4, 3],
    11: [2, 10, 9],
    12: [4, 2],
    13: [5, 3, 8],
    14: [5, 3],
    15: [9, 4, 2],
}

# Tendência de crescimento anual (simulando aumento de capacidade)
def growth_factor(date):
    years_since_start = (date - start_date).days / 365.25
    return 1.0 + 0.08 * years_since_start  # 8% crescimento anual

distributions = []
dist_id = 1
current_date = start_date

while current_date < end_date:
    month = current_date.month
    
    for plant_id, (ptype, base_energy) in plant_types.items():
        seasonal = seasonal_map[ptype][month]
        growth = growth_factor(current_date)
        
        for grid_id in plant_grid_map[plant_id]:
            # Distribuir energia proporcionalmente entre redes
            share = 1.0 / len(plant_grid_map[plant_id])
            energy = base_energy * share * seasonal * growth
            # Adicionar variação aleatória (+/- 15%)
            energy *= random.uniform(0.85, 1.15)
            energy = round(energy, 2)
            
            distributions.append((plant_id, grid_id, current_date.strftime("%Y-%m-%d"), energy))
            dist_id += 1
    
    # Avançar 1 dia (mas para não ter dados excessivos, vamos fazer semanal)
    current_date += timedelta(days=7)

# Inserir distribuições
cursor.executemany(
    "INSERT INTO Distribution (plant_id, grid_id, distribution_date, energy_supplied_kwh) VALUES (?, ?, ?, ?)",
    distributions
)

conn.commit()

# Verificar
for table in ['Company', 'Grid', 'Plant', 'Distribution']:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"{table}: {cursor.fetchone()[0]} registos")

print(f"\nBase de dados populada com sucesso!")
print(f"Período: {start_date.strftime('%Y-%m-%d')} a {(end_date - timedelta(days=1)).strftime('%Y-%m-%d')}")

conn.close()
