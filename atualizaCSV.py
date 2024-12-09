# Importa bibliotecas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd
from datetime import datetime, timezone
import requests
import pytz
import numpy as np
import os
#Teste
# Fuso horário de Brasília
brasilia_tz = pytz.timezone("America/Sao_Paulo")

# Função para pegar os dados do Weather Underground
def get_weather_data():
    WU_API_KEY = "53f353c1e4cd4445b353c1e4cdc445a9" # JAMAIS COMPARTILHAR ESSA API KEY
    STATION_ID = "ICURITIB28"
    url = f"https://api.weather.com/v2/pws/observations/current?stationId={STATION_ID}&format=json&units=m&numericPrecision=decimal&apiKey={WU_API_KEY}"
    timestamp = datetime.now(pytz.utc).astimezone(brasilia_tz)
    try:
      response = requests.get(url)
      response.raise_for_status()
      data = response.json()
      observation = data['observations'][0]
      temp = observation["metric"]["temp"]
      precip_total = observation["metric"]["precipTotal"]
      humidity = observation["humidity"]
      dew_point = observation["metric"]["dewpt"]
      solar_rad = observation["solarRadiation"]
      wind_speed = observation["metric"]["windSpeed"]
      wind_dir = observation["winddir"]
      wind_gust = observation["metric"]["windGust"]
      pressure = observation["metric"]["pressure"]
      return timestamp, temp, precip_total, humidity, dew_point, solar_rad, wind_speed, wind_dir, wind_gust, pressure
    except requests.exceptions.RequestException as e:
      print("Erro na requisição:", e)
      return timestamp, None, None, None, None, None, None, None, None, None
    except KeyError as e:
      print("Chave não encontrada nos dados da API:", e)
      return timestamp, None, None, None, None, None, None, None, None, None

# Caminho do arquivo CSV
csv_file = 'weather_data.csv'

# Verificar se o arquivo existe
if os.path.exists(csv_file):
    # Ler os dados existentes
    df = pd.read_csv(csv_file, parse_dates=['Timestamp'])
else:
    # Criar um DataFrame vazio
    df = pd.DataFrame(columns=['Timestamp', 'Temperature', 'Precip', 'Humidity', 'Dew Point', 'Radiation', 'Wind Speed', 'Wind Dir', 'Wind Gust', 'Pressure'])

# Obter os dados atuais
timestamp, temp, precip_total, humidity, dew_point, solar_rad, wind_speed, wind_dir, wind_gust, pressure = get_weather_data()

# Verificar se o timestamp já existe no DataFrame
if timestamp not in df['Timestamp'].values:
    # Criar um DataFrame com o novo dado
    new_data = pd.DataFrame({
        'Timestamp': [timestamp],
        'Temperature': [temp],
        'Precip': [precip_total],
        'Humidity': [humidity],
        'Dew Point': [dew_point],
        'Radiation': [solar_rad],
        'Wind Speed': [wind_speed],
        'Wind Dir': [wind_dir],
        'Wind Gust': [wind_gust],
        'Pressure': [pressure]
    })

    # Concatenar com o DataFrame existente
    df = pd.concat([df, new_data], ignore_index=True)

    # Filtrar para manter apenas os dados das últimas 24 horas
    now = datetime.now(brasilia_tz)
    df = df[df['Timestamp'] >= now - pd.Timedelta(hours=24)]

    # Salvar no arquivo CSV
    df.to_csv(csv_file, index=False)
    #Estacao On/Off
    if temp is not None:
        estadoEstacao = 'Online'
    else:
        estadoEstacao = 'Offline'
else:
    print("Dados já existentes para o timestamp:", timestamp)
    #Estacao On/Off
    estadoEstacao = 'Offline'

# Cálculo de mínimas e máximas a partir dos dados do DataFrame
min_temp = df['Temperature'].min()
max_temp = df['Temperature'].max()
min_humidity = df['Humidity'].min()
max_humidity = df['Humidity'].max()
min_pressure = df['Pressure'].min()
max_pressure = df['Pressure'].max()

# Configurar subplots
fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
fig.suptitle("Tempo e Extremos nas últimas 24 horas")

# Definir o colormap baseado na temperatura
c1 = plt.cm.Purples(np.linspace(0, 1, 50))
c2 = plt.cm.turbo(np.linspace(0, 1, 176))
c3 = plt.cm.get_cmap('PuRd_r')(np.linspace(0, 1, 50))
col = np.vstack((c1, c2, c3))
cmap = plt.cm.colors.ListedColormap(col)
cmap_hum = plt.cm.colors.ListedColormap(plt.cm.coolwarm(np.linspace(1, 0, 100)))
cmap_pres = plt.cm.colors.ListedColormap(plt.cm.rainbow(np.linspace(1, 0, 100)))
temp_norm = (temp + 10) / 55  # Normaliza a temperatura dos limites [-10, 45]ºC para o intervalo [0, 1]
temp_norm = np.clip(temp_norm, 0, 1)  # Garante que o valor esteja entre 0 e 1
state_color = 'red' if estadoEstacao == "Offline" else 'green'
temp_color = cmap(temp_norm)
hum_color = cmap_hum(humidity / 100)
pres_color = cmap_pres((pressure - 920) / 20)

hora_atual = f"{timestamp.hour:02d}"
minuto_atual = f"{timestamp.minute:02d}"
dia_atual = f"{timestamp.day:02d}"
mes_atual = f"{timestamp.month}"
ano_atual = f"{timestamp.year}"
fig.text(0.5, 0.99, estadoEstacao, color=state_color, fontsize=16, ha='center')
# Exibir a temperatura, umidade, P.O. e pressão acima dos plots
plt.figtext(0.5, 1.15, f"Condições meteorológicas atuais no IFUSP - Atualizado {dia_atual}/{mes_atual}/{ano_atual} às {hora_atual}:{minuto_atual}", fontsize=12, ha='center')

quadrado = plt.Rectangle((0.15, 1.03), 0.22, 0.10, transform=fig.transFigure, color=temp_color, lw=0)
fig.patches.append(quadrado)
# Definir a cor do texto com base na temperatura
text_color = 'white' if (temp >= 32 or temp < 8) else 'black'
# Usar o texto com a cor definida
plt.figtext(0.26, 1.05, f"Temperatura:\n {temp:.1f} °C", fontsize=18, ha='center', color=text_color)
plt.figtext(0.26, 1.00, f"Ponto de orvalho: {dew_point:.1f} °C", fontsize=12, ha='center', color='black')

quadrado = plt.Rectangle((0.39, 1.03), 0.22, 0.10, transform=fig.transFigure, color=hum_color, lw=0)
fig.patches.append(quadrado)
plt.figtext(0.50, 1.05, f"Umidade:\n {humidity:.0f} %", fontsize=18, ha='center', color='black')

quadrado = plt.Rectangle((0.63, 1.03), 0.22, 0.10, transform=fig.transFigure, color=pres_color, lw=0)
fig.patches.append(quadrado)
plt.figtext(0.74, 1.05, f"Pressão:\n {pressure:.1f} hPa", fontsize=18, ha='center', color='black')

plt.subplots_adjust(right=0.5)
# Exibir mínimas e máximas diárias à direita
plt.figtext(0.99, 0.83, "Temperatura", fontsize=16)
plt.figtext(0.99, 0.80, f"Mínima: {min_temp:.1f} °C", fontsize=12)
plt.figtext(0.99, 0.78, f"Máxima: {max_temp:.1f} °C", fontsize=12)
plt.figtext(0.99, 0.54, "Umidade", fontsize=16)
plt.figtext(0.99, 0.51, f"Mínima: {min_humidity:.0f} %", fontsize=12)
plt.figtext(0.99, 0.49, f"Máxima: {max_humidity:.0f} %", fontsize=12)
plt.figtext(0.99, 0.26, "Pressão", fontsize=16)
plt.figtext(0.99, 0.23, f"Mínima: {min_pressure:.1f} hPa", fontsize=12)
plt.figtext(0.99, 0.21, f"Máxima: {max_pressure:.1f} hPa", fontsize=12)

# Temperatura
axs[0].plot(df['Timestamp'], df['Temperature'], label="Temperatura", color='red', marker='o')
axs[0].plot(df['Timestamp'], df['Dew Point'], label="Ponto de orvalho", color="green", linestyle="--", marker='o',markersize=3)
axs[0].set_ylabel("Temperatura (°C)",fontsize=14)
axs[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x}"))
axs[0].legend(loc="upper left")
axs[0].grid(True)
for label in axs[0].get_yticklabels(): #Tamanho dos rótulos
    label.set_fontsize(14)

# Umidade
axs[1].plot(df['Timestamp'], df['Humidity'], color='blue', marker='o')
axs[1].set_ylabel("Umidade relativa (%)",fontsize=14)
axs[1].set_ylim([0, 110]) 
axs[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}"))
axs[1].grid(True)
for label in axs[1].get_yticklabels(): #Tamanho dos rótulos
    label.set_fontsize(14)

# Pressão
axs[2].plot(df['Timestamp'], df['Pressure'], color='black', marker='o')
axs[2].set_ylabel("Pressão (hPa)",fontsize=14)
axs[2].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}"))
axs[2].grid(True)
for label in axs[2].get_yticklabels(): #Tamanho dos rótulos
    label.set_fontsize(14)

# Formatação do eixo X
axs[2].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=brasilia_tz))
axs[2].xaxis.set_major_locator(mdates.HourLocator(interval=2))
for label in axs[2].get_xticklabels():
    label.set_fontsize(14)
plt.xlabel("Hora local",fontsize=14)
plt.gcf().autofmt_xdate()

# Configurar limites para cada eixo Y em cada subplot
axs[0].set_ylim(df['Dew Point'].min()-2, df['Temperature'].max()+2)
#axs[1].set_ylim(max(df['Humidity'].min()-10, 0), 101)
axs[2].set_ylim(df['Pressure'].min()-2, df['Pressure'].max()+2)

# Salvar o gráfico em um arquivo
plt.tight_layout()
plt.savefig('graph.png', bbox_inches='tight')
plt.close(fig)
