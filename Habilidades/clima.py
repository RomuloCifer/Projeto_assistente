import os
import requests 
import datetime
from dotenv import load_dotenv # type: ignore
#carregar a keys do .env
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
if not WEATHER_API_KEY:
    raise ValueError("Chave de API do OpenWeatherMap não encontrada.")

def obter_coordenadas(cidade):
    """Retorna (lat, lon) para uma cidade usando a API de geocoding do OpenWeatherMap.

    Arguments:
        cidade (str): nome da cidade a procurar.

    Returns:
        tuple: (lat, lon) ou (None, None) se não encontrado/erro.
    """
    url_base = f"http://api.openweathermap.org/geo/1.0/direct?q={cidade}&limit=1&appid={WEATHER_API_KEY}"
    try:
        resposta = requests.get(url_base)  # faz a requisição para a API
        resposta.raise_for_status()  # lança se houve erro HTTP
        dados = resposta.json()
        if dados:
            return dados[0]['lat'], dados[0]['lon']
        else:
            return None, None  # cidade não encontrada
    except Exception as e:
        print(f"Erro ao buscar coordenadas: {e}")
        return None, None
        
    
def obter_previsao_futuro(lat, lon, data_alvo_str):
    """Busca previsão diária futura (até 7 dias) para coordenadas específicas.

    A chamada usa o endpoint One Call (exclui current,minutely,hourly,alerts).
    """
    url_base = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={WEATHER_API_KEY}&units=metric&lang=pt_br"
    try:
        resposta = requests.get(url_base)
        resposta.raise_for_status()
        dados = resposta.json()
        data_alvo = datetime.datetime.strptime(data_alvo_str, "%Y-%m-%d").date()  # converte string para date

        for previsao_diaria in dados['daily']:
            data_previsao = datetime.date.fromtimestamp(previsao_diaria['dt'])  # timestamp -> date
            if data_previsao == data_alvo:
                temp_max = previsao_diaria['temp']['max']
                descricao = previsao_diaria['weather'][0]['description']
                return f"A previsão para{data_alvo_str} é de máxima de {temp_max:.0f} graus com {descricao}."

        return "Desculpe, não tenho dados para esta data."
    except Exception as e:
        print(f"Erro ao buscar previsão futura: {e}")
        return "Desculpe, tive um problema ao buscar a previsão futura."
    
def obter_previsao_tempo(cidade: str):
    """Retorna frase com previsão do tempo atual para uma cidade.

    Usa o endpoint /data/2.5/weather e retorna mensagem amigável em português.
    """
    url_base = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={WEATHER_API_KEY}&units=metric&lang=pt_br"

    try:
        resposta = requests.get(url_base)  # faz a requisição para a API
        resposta.raise_for_status()
        dados_clima = resposta.json()  # converte a resposta em JSON
        temperatura = dados_clima['main']['temp']  # extrai temperatura
        descricao = dados_clima['weather'][0]['description']  # descrição do tempo
        frase_clima = f"No momento, em {cidade}, está fazendo {temperatura} graus Celsius e está {descricao}."
        return frase_clima

    except requests.exceptions.HTTPError as http_err:
        if resposta.status_code == 404:
            return "Cidade não encontrada. Por favor, verifique o nome da cidade."
        else:
            return f"Erro HTTP ao obter a previsão do tempo: {http_err}"
    except Exception as e:
        print(f"Erro ao buscar previsão do tempo: {e}")
        return "Desculpe, estou com problemas para acessar a previsão do tempo agora."