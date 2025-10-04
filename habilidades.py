#fazer chamadas API
import requests # type: ignore
import os
from dotenv import load_dotenv # type: ignore
#carregar a keys do .env
load_dotenv()
#ACCESS PORCUPINE

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
if not WEATHER_API_KEY:
    raise ValueError("Chave de API do OpenWeatherMap não encontrada. Verifique seu arquivo .env")
def obter_previsao_tempo(cidade="Nova Friburgo"):
    """Obtém a previsão do tempo para uma cidade específica usando o OpenWeatherMap"""
    url_base = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={WEATHER_API_KEY}&units=metric&lang=pt_br"

    try:
        #faz a requisição para a API
        resposta = requests.get(url_base)
        #erro caso não dê certo
        resposta.raise_for_status()

        #converte a resposta em JSON
        dados_clima = resposta.json()

        #Extrai as informações do dicionario
        temperatura = dados_clima['main']['temp']
        descricao = dados_clima['weather'][0]['description']

        #frase para o assistente
        frase_clima = f"No momento, em {cidade}, está fazendo {temperatura} graus Celsius com {descricao}."
        return frase_clima
    except requests.exceptions.HTTPError as http_err:
        if resposta.status_code == 404:
            return "Cidade não encontrada. Por favor, verifique o nome da cidade."
        else:
            return f"Erro HTTP ao obter a previsão do tempo: {http_err}"
    #erros possiveis, como conexão
    except Exception as e:
        print(f"Erro ao buscar previsão do tempo: {e}")
        return "Desculpe, estou com problemas para acessar a previsão do tempo agora."

        