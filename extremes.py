import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd
from datetime import datetime
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
timestamp = datetime.now(timezone.utc).astimezone(brasilia_tz)
data_formatada = timestamp.strftime("%Y-%m-%d")

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

# Verificar se a data já existe no DataFrame
if pd.to_datetime(data_formatada).date() not in df['Date'].values:
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
    df.to_csv(csv_file, index=False)
    print(f"Dados de {data_formatada} adicionados ao arquivo {csv_file}.")
else:
    print(f"Dados de {data_formatada} já existem no arquivo {csv_file}.")

# Determinar a data de ontem no formato YYYY-MM-DD
yesterday = (datetime.now(brasilia_tz) - timedelta(days=1)).strftime("%Y-%m-%d")

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

    # Criar o gráfico
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axis('off')  # Ocultar os eixos

    # Texto do resumo
    summary_text = (
        f"Resumo do dia anterior ({yesterday}):\n\n"
        f"🌡️ Temperatura mínima: {min_temp:.1f} °C\n"
        f"🌡️ Temperatura máxima: {max_temp:.1f} °C\n"
        f"🌡️ Temperatura média: {mean_temp:.1f} °C\n"
        f"☔ Precipitação acumulada: {precip_total:.1f} mm"
    )

    # Adicionar texto ao gráfico
    ax.text(0.5, 0.5, summary_text, fontsize=14, ha='center', va='center', 
            bbox=dict(facecolor='lightblue', alpha=0.5))

    # Título
    plt.title("Resumo Meteorológico de ontem", fontsize=16, pad=20)

    # Salvar o gráfico em um arquivo
    plt.tight_layout()
    plt.savefig('graph.png', bbox_inches='tight')
    plt.close(fig)

