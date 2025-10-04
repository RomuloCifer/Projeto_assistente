#fazer chamadas API
import requests # type: ignore
import os
import google.generativeai as genai # type: ignore
#precisamos do datetime para pegar a hora e lidar com comandos do tipo "qual a previsão para amanhã?"
import datetime 
from dotenv import load_dotenv # type: ignore
#carregar a keys do .env
load_dotenv()
#ACCESS PORCUPINE

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")
if not WEATHER_API_KEY or not GEMINI_API_KEY:
    raise ValueError("Chave de API do OpenWeatherMap ou Gemini não encontrada. Verifique seu arquivo .env")

#configurar a API Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-flash-latest")

def analisar_comando_gemini(comando):
    #pegar a data de hoje
    data_hoje = datetime.datetime.now()
    dias_semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
    dia_semana_hoje = dias_semana[data_hoje.weekday()]
    """Usa a API Gemini para analisar o comando e determinar a ação apropriada"""
    
    #Um prompt para o gemini entender o comando.
    prompt = f"""
    Analise o comando para um assistente virtual. Hoje é {dia_semana_hoje}, dia {data_hoje.strftime("%Y-%m-%d")}.
    O comando é: "{comando}"

    Extraia as informações e retorne APENAS um objeto JSON com:
    1. "intent": A intenção. Deve ser 'get_weather', 'get_time', 'exit', ou 'unknown'.
    2. "location": A cidade ou local.
    3. "date": A data exata no formato AAAA-MM-DD. Use o contexto de hoje para calcular datas relativas como 'amanhã', 'próximo sábado', 'depois de amanhã'.

    Exemplos:
    - Comando: "previsão para o próximo sábado em salvador", Hoje é Sábado, 2025-10-04 -> JSON: {{"intent": "get_weather", "location": "Salvador", "date": "2025-10-11"}}
    - Comando: "como vai estar o tempo depois de amanhã em Curitiba", Hoje é 2025-10-04 -> JSON: {{"intent": "get_weather", "location": "Curitiba", "date": "2025-10-06"}}
    - Comando: "clima para hoje" -> JSON: {{"intent": "get_weather", "location": null, "date": "{data_hoje.strftime('%Y-%m-%d')}"}}

    Analise o comando fornecido.
    """
    try:
        resposta = model.generate_content(prompt)
        # O .text pode vir com marcações de JSON, então aqui nós limpamos isso.
        json_text = resposta.text.strip().replace("```json", "").replace("```", "")
        import json
        #retorna como dicionario, para facilitar o uso. Podemos pegar o intent por exemplo com resultado['intent']
        return json.loads(json_text)
    except Exception as e:
        print("Erro ao analisar comando com Gemini:", e)
        return {"intent": "unknown", "location": None, "date": None}
    

def obter_previsao_tempo(cidade: str):
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
        frase_clima = f"No momento, em {cidade}, está fazendo {temperatura} graus Celsius e está {descricao}."
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

        