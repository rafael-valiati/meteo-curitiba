import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd
from datetime import datetime, timedelta, timezone
import requests
import pytz
import numpy as np
import os

# Fuso horário de Brasília
brasilia_tz = pytz.timezone("America/Sao_Paulo")

# Função para pegar mínimas e máximas diárias
def get_daily_min_max():
    WU_API_KEY = os.getenv('API_KEY') # JAMAIS COMPARTILHAR ESSA API KEY
    STATION_ID = "ICURITIB28"
    current_date = datetime.now(brasilia_tz)
    yesterday_date = current_date - timedelta(days=1)
    yesterday_formatted = yesterday_date.strftime("%Y%m%d")
    url = f"https://api.weather.com/v2/pws/history/daily?stationId={STATION_ID}&format=json&units=m&numericPrecision=decimal&date={yesterday_formatted}&apiKey={WU_API_KEY}"
    try:
      response = requests.get(url)
      response.raise_for_status()
      data = response.json()
      #print(data)
      summary = data['observations'][0]["metric"]
      min_temp = summary["tempLow"]
      max_temp = summary["tempHigh"]
      mean_temp = summary["tempAvg"]
      precip_total = summary["precipTotal"]
      return min_temp, max_temp, mean_temp, precip_total
    except requests.exceptions.RequestException as e:
      print("Erro na requisição:", e)
      return None, None, None, None
    except KeyError as e:
      print("Chave não encontrada nos dados da API:", e)
      return None, None, None, None

# Obter os extremos diários de ontem
min_temp, max_temp, mean_temp, precip_total = get_daily_min_max()
timestamp = datetime.now(timezone.utc).astimezone(brasilia_tz) - timedelta(days=1)
data_formatada = timestamp.date()  # Obter apenas a data (YYYY-MM-DD) como datetime.date

# Caminho do arquivo CSV
csv_file = 'month_data.csv'

# Verificar se o arquivo existe
if os.path.exists(csv_file):
    # Ler os dados existentes
    df = pd.read_csv(csv_file, parse_dates=['Date'])
    df['Date'] = df['Date'].dt.date  # Apenas data (sem hora e sem timezone)
else:
    # Criar um DataFrame vazio
    df = pd.DataFrame(columns=['Date', 'MinTemp', 'MaxTemp', 'AvgTemp', 'Precip'])
    print("Arquivo CSV não encontrado. Criando um arquivo vazio...")
    df.to_csv(csv_file, index=False)

# Obter a data atual no formato YYYY-MM
current_month = timestamp.strftime("%Y-%m")

# Obter a data atual no formato YYYY-MM
current_month = timestamp.strftime("%Y-%m")
# Filtrar os dados do DataFrame para manter apenas os registros do mesmo mês
df = df[df['Date'].apply(lambda x: x.strftime("%Y-%m")) == current_month]

# Verificar se a data já existe no DataFrame
if data_formatada not in df['Date'].values:
    # Criar um DataFrame com o novo dado
    new_data = pd.DataFrame({
        'Date': [data_formatada],
        'MinTemp': [min_temp],
        'MaxTemp': [max_temp],
        'AvgTemp': [mean_temp],
        'Precip': [precip_total]
    })

    # Concatenar com o DataFrame existente
    df = pd.concat([df, new_data], ignore_index=True)

    # Salvar de volta no CSV
    #df['Date'] = pd.to_datetime(df['Date']).dt.strftime("%Y-%m-%d")  # Salvar no formato desejado
    df.to_csv(csv_file, index=False, date_format='%Y-%m-%d')
    print(f"Dados de {data_formatada} adicionados ao arquivo {csv_file}.")
else:
    print(f"Dados de {data_formatada} já existem no arquivo {csv_file}.")

# Determinar a data de ontem no formato YYYY-MM-DD
yesterday = (datetime.now(brasilia_tz) - timedelta(days=1)).date()

# Obter os dados do dia anterior
daily_data = df[df['Date'] == yesterday]

if daily_data.empty:
    print(f"Nenhum dado encontrado para {yesterday}.")
else:
    # Extrair valores do dia anterior
    min_temp = daily_data['MinTemp'].iloc[0]
    max_temp = daily_data['MaxTemp'].iloc[0]
    mean_temp = daily_data['AvgTemp'].iloc[0]
    precip_total = daily_data['Precip'].iloc[0]

    # Dados para o mês inteiro
    min_min = df['MinTemp'].min()
    min_max = df['MinTemp'].max()
    max_min = df['MaxTemp'].min()
    max_max = df['MaxTemp'].max()
    avg_min = df['MinTemp'].mean()
    avg_max = df['MaxTemp'].mean()
    media_horaria = df['AvgTemp'].mean()
    precip_soma_mes = df['Precip'].sum()

    # Criar o gráfico
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axis('off')  # Ocultar os eixos

    # Título
    plt.title("Resumo meteorológico de ontem", fontsize=20, pad=20)

    # Texto do resumo
    summary_text = (
        #f"Resumo do dia anterior ({yesterday}):\n\n"
        f"Temperatura mínima: {min_temp:.1f} °C\n"
        f"Temperatura máxima: {max_temp:.1f} °C\n"
        #f"Temperatura média: {mean_temp:.1f} °C\n"
        f"Chuva acumulada: {precip_total:.1f} mm"
    )

    # Adicionar texto ao gráfico
    ax.text(0.5, 0.9, summary_text, fontsize=14, ha='center', va='center', 
            bbox=dict(facecolor='lightblue', alpha=0.5))

    quadrado = plt.Rectangle((0.2, 0.24), 0.22, 0.28, transform=fig.transFigure, lw=1, edgecolor='black', facecolor='lightblue', alpha=0.5)
    fig.patches.append(quadrado)
    quadrado = plt.Rectangle((0.58, 0.24), 0.22, 0.28, transform=fig.transFigure, lw=1, edgecolor='black', facecolor='lightcoral', alpha=0.5)
    fig.patches.append(quadrado)

    ax.text(0.5, 0.68, "Resumo do mês atual até ontem", fontsize=20, ha='center', va='center')
    ax.text(0.3, 0.54, "Mínimas", fontsize=14, ha='center', va='center')
    ax.text(0.7, 0.54, "Máximas", fontsize=14, ha='center', va='center')

    ax.text(0.3, 0.44, f"↑ {min_max:.1f} ºC", fontsize=10, color='red', ha='center', va='center')
    ax.text(0.7, 0.44, f"↑ {max_max:.1f} ºC", fontsize=10, color='red', ha='center', va='center')
    ax.text(0.3, 0.3, f"↓ {min_min:.1f} ºC", fontsize=10, color='blue', ha='center', va='center')
    ax.text(0.7, 0.3, f"↓ {max_min:.1f} ºC", fontsize=10, color='blue', ha='center', va='center')
    ax.text(0.3, 0.37, f"{avg_min:.1f} ºC", fontsize=18, ha='center', va='center')
    ax.text(0.7, 0.37, f"{avg_max:.1f} ºC", fontsize=18, ha='center', va='center')

    ax.text(0.5, 0.12, f"Temperatura média: {media_horaria:.1f} ºC\n", fontsize=16, ha='center', va='center')
    ax.text(0.5, 0.05, f"Precipitação total: {precip_soma_mes:.1f} mm\n", fontsize=16, ha='center', va='center')

    # Salvar o gráfico em um arquivo
    plt.tight_layout()
    plt.savefig('extremes_graph.png', bbox_inches='tight')
    plt.close(fig)

