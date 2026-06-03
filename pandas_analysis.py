import pandas as pd
import sqlite3

DB_PATH = 'TrabalhoPCII.db'

# 1. CARREGAR DADOS

conn = sqlite3.connect(DB_PATH)

dist    = pd.read_sql('SELECT * FROM Distribution', conn)
grid    = pd.read_sql('SELECT * FROM Grid',         conn)
plant   = pd.read_sql('SELECT * FROM Plant',        conn)
company = pd.read_sql('SELECT * FROM Company',      conn)

conn.close()

dist['distribution_date'] = pd.to_datetime(dist['distribution_date'])

dist['month']   = dist['distribution_date'].dt.to_period('M').astype(str)
dist['weekday'] = dist['distribution_date'].dt.day_name()
dist['quarter'] = dist['distribution_date'].dt.quarter.map(
                      {1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4'})

df = (dist
      .merge(grid,    on='grid_id')
      .merge(plant,   on='plant_id')
      .merge(company, on='company_id'))

df['plant_label'] = 'Central #' + df['plant_id'].astype(str)

print("=" * 60)
print("DADOS CARREGADOS")
print("=" * 60)
print(f"  Shape             : {df.shape}")
print(f"  Colunas           : {df.columns.tolist()}")

# 2. QUALIDADE DOS DADOS

print("\n" + "=" * 60)
print("QUALIDADE DOS DADOS — Valores nulos por coluna")
print("=" * 60)
nulls = df.isnull().sum()
print(nulls)

# 3. ESTATÍSTICAS DESCRITIVAS GERAIS

print("\n" + "=" * 60)
print("ESTATÍSTICAS DESCRITIVAS — energy_supplied_kwh")
print("=" * 60)
print(df['energy_supplied_kwh'].describe().round(2))


total = df['energy_supplied_kwh'].sum()
print(f"\n  Total distribuído (kWh)  : {total:>18,.2f}")
print(f"  Nº de distribuições      : {len(df):>18,}")
print(f"  Nº de redes únicas       : {df['grid_id'].nunique():>18,}")
print(f"  Nº de centrais únicas    : {df['plant_id'].nunique():>18,}")
print(f"  Nº de empresas únicas    : {df['company_id'].nunique():>18,}")
print(f"  Período                  :  "
      f"{df['distribution_date'].min().date()} → "
      f"{df['distribution_date'].max().date()}")

# 4. ANÁLISE 1 — Energia distribuída por mês

print("\n" + "=" * 60)
print("ANÁLISE 1 — Energia por Mês (kWh)")
print("=" * 60)

monthly = (df.groupby('month')['energy_supplied_kwh']
             .agg(total='sum', mean='mean', n_distribuicoes='count')
             .reset_index()
             .sort_values('month'))

monthly['total_M_kwh'] = (monthly['total'] / 1_000_000).round(3)
print(monthly[['month', 'total_M_kwh', 'mean', 'n_distribuicoes']].to_string(index=False))

# 5. ANÁLISE 2 — Energia por Rede (Top 10)

print("\n" + "=" * 60)
print("ANÁLISE 2 — Top 10 Redes por kWh Total")
print("=" * 60)

grid_energy = (df.groupby('grid_name')['energy_supplied_kwh']
                 .sum()
                 .nlargest(10)
                 .reset_index()
                 .rename(columns={'energy_supplied_kwh': 'total_kwh'})
                 .sort_values('total_kwh', ascending=False))
grid_energy['total_kwh'] = grid_energy['total_kwh'].round(2)
print(grid_energy.to_string(index=False))

# 6. ANÁLISE 3 — Energia por Central (Top 10)

print("\n" + "=" * 60)
print("ANÁLISE 3 — Top 10 Centrais por kWh Total")
print("=" * 60)

plant_energy = (df.groupby('plant_label')['energy_supplied_kwh']
                  .sum()
                  .nlargest(10)
                  .reset_index()
                  .rename(columns={'energy_supplied_kwh': 'total_kwh'})
                  .sort_values('total_kwh', ascending=False))
plant_energy['total_kwh'] = plant_energy['total_kwh'].round(2)
print(plant_energy.to_string(index=False))



# 7. ANÁLISE 4 — Energia por Empresa (Top 8)

print("\n" + "=" * 60)
print("ANÁLISE 4 — Top 8 Empresas por kWh Total")
print("=" * 60)

company_energy = (df.groupby('company_name')['energy_supplied_kwh']
                    .sum()
                    .nlargest(8)
                    .reset_index()
                    .rename(columns={'energy_supplied_kwh': 'total_kwh'}))
company_energy['total_kwh']  = company_energy['total_kwh'].round(2)
company_energy['quota_%']    = (
    company_energy['total_kwh'] / total * 100).round(2)
print(company_energy.to_string(index=False))


# 8. ANÁLISE 5 — Energia por Trimestre

print("\n" + "=" * 60)
print("ANÁLISE 5 — Energia por Trimestre")
print("=" * 60)

quarterly = (df.groupby('quarter')['energy_supplied_kwh']
               .agg(total='sum', mean='mean', n_distribuicoes='count')
               .reset_index())
quarterly['total_M_kwh'] = (quarterly['total'] / 1_000_000).round(3)
print(quarterly[['quarter', 'total_M_kwh', 'mean', 'n_distribuicoes']].to_string(index=False))


# 9. ANÁLISE 6 — Histograma de distribuições por intervalo de kWh

print("\n" + "=" * 60)
print("ANÁLISE 6 — Frequência por intervalo de kWh")
print("=" * 60)

bins         = pd.cut(df['energy_supplied_kwh'], bins=10)
hist_series  = df.groupby(bins, observed=True)['energy_supplied_kwh'].count()
hist         = pd.DataFrame({
                   'intervalo':      hist_series.index.astype(str),
                   'n_distribuicoes': hist_series.values
               })
hist['pct_%'] = (hist['n_distribuicoes'] / len(df) * 100).round(1)
print(hist.to_string(index=False))


# 10. ANÁLISE 7 — Média de energia por dia da semana

print("\n" + "=" * 60)
print("ANÁLISE 7 — Média de energia por dia da semana (kWh)")
print("=" * 60)

order   = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
weekday = (df.groupby('weekday')['energy_supplied_kwh']
             .mean()
             .reindex(order)
             .reset_index()
             .rename(columns={'energy_supplied_kwh': 'mean_kwh'}))
weekday['mean_kwh'] = weekday['mean_kwh'].round(2)
weekday['desvio_media_%'] = (
    (weekday['mean_kwh'] - weekday['mean_kwh'].mean())
    / weekday['mean_kwh'].mean() * 100).round(2)
print(weekday.to_string(index=False))


# 11. ANÁLISE 8 — Quota por empresa (Top 5)

print("\n" + "=" * 60)
print("ANÁLISE 8 — Quota de energia por empresa (Top 5)")
print("=" * 60)

top5 = (df.groupby('company_name')['energy_supplied_kwh']
          .sum()
          .nlargest(5)
          .reset_index()
          .rename(columns={'energy_supplied_kwh': 'total_kwh'}))
top5['total_kwh'] = top5['total_kwh'].round(2)
top5['quota_%']   = (top5['total_kwh'] / total * 100).round(2)
print(top5.to_string(index=False))
print(f"\n  Top 5 representam: {top5['quota_%'].sum():.1f}% do total distribuído")


print("\n" + "=" * 60)
print("FIM DA ANÁLISE — 8 análises concluídas")
print("=" * 60)
