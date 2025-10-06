import os
import datetime
import json
from dotenv import load_dotenv # type: ignore

#carregar a keys do .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Chave de API do Gemini não encontrada.")



def analisar_comando_gemini(comando):
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-flash-latest")
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
    1. "intent": A intenção. Deve ser 'get_weather', 'get_time', 'exit', 'tocar_musica', 'iniciar_tradutor', 'parar_tradutor', ou 'unknown'.
    2. "location": A cidade ou local. Pode ser nulo se não especificado.
    3. "date": A data exata no formato AAAA-MM-DD. Use o contexto de hoje.
    4. "music_title": O nome da música e/ou artista. Nulo se não for a intenção.

    Exemplos de raciocínio (não use essas datas, são apenas para ilustrar o formato):
    - Se o comando for "previsão para o próximo sábado em salvador", a data deve ser "2025-10-11".
    - Se o comando for "toque bohemian rhapsody queen", a intenção deve ser "tocar_musica" e "music_title" deve ser "bohemian rhapsody queen".
    - Se o comando for "ativar modo de tradução" ou "preciso traduzir algo", a intenção deve ser "iniciar_tradutor".
    - Se o comando for "desativar modo de tradução", a intenção deve ser "parar_tradutor".

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
        return {"intent": "unknown", "location": None, "date": None, "music_title": None}