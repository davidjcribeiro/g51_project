from flask import render_template, session
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'TrabalhoPCII.db')

def _load_data():
    """Load and join all tables into a single enriched DataFrame."""
    engine = create_engine('sqlite:///' + DB_PATH)

    dist    = pd.read_sql('Distribution', con=engine)
    grid    = pd.read_sql('Grid',         con=engine)
    plant   = pd.read_sql('Plant',        con=engine)
    company = pd.read_sql('Company',      con=engine)

    dist['distribution_date'] = pd.to_datetime(dist['distribution_date'])
    dist['month']    = dist['distribution_date'].dt.to_period('M').astype(str)
    dist['weekday']  = dist['distribution_date'].dt.day_name()
    dist['quarter']  = dist['distribution_date'].dt.quarter.map(
                           {1:'Q1', 2:'Q2', 3:'Q3', 4:'Q4'})

    df = (dist
          .merge(grid,    on='grid_id')
          .merge(plant,   on='plant_id')
          .merge(company, on='company_id'))

    df['plant_label'] = 'Central #' + df['plant_id'].astype(str)
    return df

# Chart 1 – Energia distribuída por mês (line + mean)

def apps_monthly():
    df = _load_data()
    monthly = (df.groupby('month')['energy_supplied_kwh']
                 .agg(total='sum', mean='mean')
                 .reset_index()
                 .sort_values('month'))

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=monthly['month'], y=monthly['total'],
                   name='Total (kWh)', mode='lines+markers',
                   line=dict(color='#378ADD', width=2),
                   fill='tozeroy', fillcolor='rgba(55,138,221,0.08)'),
        secondary_y=False)
    fig.add_trace(
        go.Scatter(x=monthly['month'], y=monthly['mean'],
                   name='Média (kWh)', mode='lines+markers',
                   line=dict(color='#D4537E', dash='dash', width=2)),
        secondary_y=True)

    fig.update_layout(title='Energia Distribuída por Mês (kWh total)',
                      xaxis_title='Mês', template='plotly_white',
                      legend=dict(orientation='h', y=1.1))
    fig.update_yaxes(title_text='Total (kWh)', secondary_y=False)
    fig.update_yaxes(title_text='Média (kWh)', secondary_y=True)

    plot_div = fig.to_html(full_html=False, div_id='monthly-plot')
    return render_template('dashboard.html', plot_div=plot_div,
                           chart_title='Energia por Mês',
                           ulogin=session.get('username'))

# Chart 2 – Energia por Rede (top 10 bar)

def apps_grid():
    df = _load_data()
    grid_energy = (df.groupby('grid_name')['energy_supplied_kwh']
                     .sum()
                     .nlargest(10)
                     .reset_index()
                     .sort_values('energy_supplied_kwh'))

    fig = px.bar(grid_energy, x='energy_supplied_kwh', y='grid_name',
                 orientation='h',
                 labels={'energy_supplied_kwh': 'kWh Total',
                         'grid_name': 'Rede'},
                 title='Energia por Rede (kWh total) — Top 10',
                 color='energy_supplied_kwh',
                 color_continuous_scale='Blues')
    fig.update_layout(template='plotly_white', coloraxis_showscale=False)

    plot_div = fig.to_html(full_html=False, div_id='grid-plot')
    return render_template('dashboard.html', plot_div=plot_div,
                           chart_title='Energia por Rede',
                           ulogin=session.get('username'))

# Chart 3 – Energia por Central (top 10 bar)

def apps_plant():
    df = _load_data()
    plant_energy = (df.groupby('plant_label')['energy_supplied_kwh']
                      .sum()
                      .nlargest(10)
                      .reset_index()
                      .sort_values('energy_supplied_kwh'))

    fig = px.bar(plant_energy, x='energy_supplied_kwh', y='plant_label',
                 orientation='h',
                 labels={'energy_supplied_kwh': 'kWh Total',
                         'plant_label': 'Central'},
                 title='Energia por Central (kWh total) — Top 10',
                 color='energy_supplied_kwh',
                 color_continuous_scale='Teal')
    fig.update_layout(template='plotly_white', coloraxis_showscale=False)

    plot_div = fig.to_html(full_html=False, div_id='plant-plot')
    return render_template('dashboard.html', plot_div=plot_div,
                           chart_title='Energia por Central',
                           ulogin=session.get('username'))

# Chart 4 – Energia por Empresa (top 8)

def apps_company():
    df = _load_data()
    company_energy = (df.groupby('company_name')['energy_supplied_kwh']
                        .sum()
                        .nlargest(8)
                        .reset_index())

    fig = px.bar(company_energy, x='company_name', y='energy_supplied_kwh',
                 labels={'energy_supplied_kwh': 'kWh Total',
                         'company_name': 'Empresa'},
                 title='Energia por Empresa (kWh total) — Top 8',
                 color='company_name')
    fig.update_layout(template='plotly_white', showlegend=False,
                      xaxis_tickangle=-30)

    plot_div = fig.to_html(full_html=False, div_id='company-plot')
    return render_template('dashboard.html', plot_div=plot_div,
                           chart_title='Energia por Empresa',
                           ulogin=session.get('username'))

# Chart 5 – Distribuição por Trimestre

def apps_quarterly():
    df = _load_data()
    quarterly = (df.groupby('quarter')['energy_supplied_kwh']
                   .sum()
                   .reset_index())

    fig = px.bar(quarterly, x='quarter', y='energy_supplied_kwh',
                 labels={'energy_supplied_kwh': 'kWh Total', 'quarter': 'Trimestre'},
                 title='Energia Distribuída por Trimestre',
                 color='quarter',
                 color_discrete_sequence=['#378ADD','#1D9E75','#D4537E','#EF9F27'])
    fig.update_layout(template='plotly_white', showlegend=False)

    plot_div = fig.to_html(full_html=False, div_id='quarterly-plot')
    return render_template('dashboard.html', plot_div=plot_div,
                           chart_title='Energia por Trimestre',
                           ulogin=session.get('username'))

# Chart 6 – Histograma de distribuições

def apps_histogram():
    df = _load_data()

    fig = px.histogram(df, x='energy_supplied_kwh', nbins=10,
                       labels={'energy_supplied_kwh': 'kWh por distribuição',
                               'count': 'Nº de distribuições'},
                       title='Histograma de Distribuições de Energia')
    fig.update_traces(marker_color='#378ADD', marker_line_color='#185FA5',
                      marker_line_width=1)
    fig.update_layout(template='plotly_white')

    plot_div = fig.to_html(full_html=False, div_id='hist-plot')
    return render_template('dashboard.html', plot_div=plot_div,
                           chart_title='Histograma de Energia',
                           ulogin=session.get('username'))

# Chart 7 – Média por dia da semana

def apps_weekday():
    df = _load_data()
    order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    pt_names = {'Monday':'Seg','Tuesday':'Ter','Wednesday':'Qua',
                'Thursday':'Qui','Friday':'Sex','Saturday':'Sáb','Sunday':'Dom'}
    weekday = (df.groupby('weekday')['energy_supplied_kwh']
                 .mean()
                 .reindex(order)
                 .reset_index())
    weekday['weekday'] = weekday['weekday'].map(pt_names)

    fig = px.line_polar(weekday, r='energy_supplied_kwh', theta='weekday',
                        line_close=True,
                        title='Média de Energia por Dia da Semana (kWh)')
    fig.update_traces(fill='toself', fillcolor='rgba(29,158,117,0.15)',
                      line_color='#1D9E75')
    fig.update_layout(template='plotly_white')

    plot_div = fig.to_html(full_html=False, div_id='weekday-plot')
    return render_template('dashboard.html', plot_div=plot_div,
                           chart_title='Padrão Semanal',
                           ulogin=session.get('username'))

# Chart 8 – Quota por empresa (donut)

def apps_donut():
    df = _load_data()
    top5 = (df.groupby('company_name')['energy_supplied_kwh']
              .sum()
              .nlargest(5)
              .reset_index())

    fig = px.pie(top5, names='company_name', values='energy_supplied_kwh',
                 hole=0.45,
                 title='Quota de Energia por Empresa (Top 5)',
                 color_discrete_sequence=['#378ADD','#1D9E75','#D4537E',
                                          '#EF9F27','#534AB7'])
    fig.update_layout(template='plotly_white')

    plot_div = fig.to_html(full_html=False, div_id='donut-plot')
    return render_template('dashboard.html', plot_div=plot_div,
                           chart_title='Quota por Empresa',
                           ulogin=session.get('username'))
