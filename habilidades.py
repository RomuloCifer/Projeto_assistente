#fazer chamadas API
import requests # type: ignore
import os
import google.generativeai as genai # type: ignore
#precisamos do datetime para pegar a hora e lidar com comandos do tipo "qual a previsão para amanhã?"
import datetime 
from googleapiclient.discovery import build # type: ignore
from dotenv import load_dotenv # type: ignore
#carregar a keys do .env
load_dotenv()
#ACCESS PORCUPINE

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not WEATHER_API_KEY or not GEMINI_API_KEY or not YOUTUBE_API_KEY:
    raise ValueError("Chave de API do OpenWeatherMap, Gemini ou YouTube não encontrada. Verifique seu arquivo .env")

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
    1. "intent": A intenção. Deve ser 'get_weather', 'get_time', 'exit', 'tocar_musica', ou 'unknown'.
    2. "location": A cidade ou local. Pode ser nulo se não especificado.
    3. "date": A data exata no formato AAAA-MM-DD. Use o contexto de hoje.
    4. "music_title": O nome da música e/ou artista. Nulo se não for a intenção.

    Exemplos de raciocínio (não use essas datas, são apenas para ilustrar o formato):
    - Se o comando for "previsão para o próximo sábado em salvador", a data deve ser "2025-10-11".
    - Se o comando for "como vai estar o tempo depois de amanhã em Curitiba", a data deve ser "2025-10-06".
    - Se o comando for "toque bohemian rhapsody queen", a intenção deve ser "tocar_musica" e "music_title" deve ser "bohemian rhapsody queen".
    - Se o comando for "clima para hoje", a data deve ser a data de hoje fornecida acima.

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
    
    #Obter coordenada da cidade, para funcionar comandos de clima mais avançados
def obter_coordenadas(cidade):
    url_base = f"http://api.openweathermap.org/geo/1.0/direct?q={cidade}&limit=1&appid={WEATHER_API_KEY}"
    try:
        #faz a requisição para a API
        resposta = requests.get(url_base)
        #erro caso não dê certo
        resposta.raise_for_status()
        dados = resposta.json()
        if dados:
            return dados[0]['lat'], dados[0]['lon']
        else: #se a cidade não for encontrada
            return None, None
    except Exception as e:
        print(f"Erro ao buscar coordenadas: {e}")
        return None, None
        
    
def obter_previsao_futuro(lat, lon, data_alvo_str):
    #Pegamos a previsão de hoje+7 dias / além de excluir dados desnecessário como hora, alerta, etc
    url_base = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={WEATHER_API_KEY}&units=metric&lang=pt_br"
    try:
        resposta = requests.get(url_base)
        resposta.raise_for_status()
        dados = resposta.json()
        #transforma a string da data alvo em objeto date
        data_alvo = datetime.datetime.strptime(data_alvo_str, "%Y-%m-%d").date()

        #procura a data na previsão diária
        for previsao_diaria in dados['daily']:
            #converte a data da previsão (timestamp) em objeto date (numeros de segundos desde 1970 Unix Time)
            data_previsao = datetime.date.fromtimestamp(previsao_diaria['dt'])
            #aqui verifica se a data da previsão é a que queremos
            if data_previsao == data_alvo:
                #se for, pega a temp. max e descrição do tempo.
                temp_max = previsao_diaria['temp']['max']
                descricao = previsao_diaria['weather'][0]['description']
                #depois de encontrar o dia certo, pega a temperatura máxima e a descrição do tempo
                return f"A previsão para{data_alvo_str} é de máxima de {temp_max:.0f} graus com {descricao}."
        #se o loop terminar sem achar a data.
        return "Desculpe, não tenho dados para esta data."
    except Exception as e:
        print(f"Erro ao buscar previsão futura: {e}")
        return "Desculpe, tive um problema ao buscar a previsão futura."
    
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

def pesquisar_musica_youtube(nome_musica):
    """Busca uma música no Youtube usando a API do Youtube e retorna o link do primeiro resultado"""
    try:
        #Inicia o serviço da API do youtube
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        #faz a chamada para a API
        request = youtube.search().list(
            q=nome_musica,
            part='snippet', # informações básicas como título, descrição, nome do canal, etc.
            maxResults=5, # 5 primeiros resultados
            type='video',
            topicId='/m/04rlf'  # ID do google para Música. (melhora a relevância dos resultados)
        )
        #Agora enviamos a requisição
        response = request.execute()
        #A resposta vem com vários dados, o 'items' é a lista de vídeos encontrados
        videos = response.get('items', [])
        #se a lista vier vazia.
        if not videos:
            return None
        prioridades = ['Official Music Video', 'Official Video', 'Music Video', 'Audio', 'Lyric Video']
        # Criamos uma lista para armazenar os resultados válidos
        resultados_validos = []
        
        #Uma filtragem iniciar para garantir somente vídeos válidos, ignorando canais ou playlists
        for item in videos:
            if 'videoId' in item['id']:
                resultados_validos.append(item)
        if not resultados_validos:
            return None
        #passamos pelos resultados válidos procurando por títulos prioritários
        for video in resultados_validos:
            titulo_video = video['snippet']['title'].lower()
            for p in prioridades:
                if p.lower() in titulo_video:
                    video_id = video['id']['videoId']
                    # Se encontrarmos um vídeo prioritário, informamos no console e o retornamos imediatamente.
                    print(f"Resultado priorizado encontrado: {video['snippet']['title']}")
                    return video['id']['videoId'] # O ID do vídeo é o que precisamos para a URL.
                #Se não encontrar nada prioritário, retorna o primeiro resultado.
                return resultados_validos[0]['id']['videoId']
    except Exception as e:
        print(f"Erro ao buscar música no YouTube: {e}")
        return None
