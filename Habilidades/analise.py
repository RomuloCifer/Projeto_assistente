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
Sua tarefa é analisar um comando de voz para um assistente virtual e extrair suas intenções e entidades.
O comando foi recebido exatamente em: {dia_semana_hoje}, {data_hoje.strftime("%Y-%m-%d às %H:%M")}. Use esta data como referência para qualquer cálculo de tempo.

Analise o comando de voz abaixo e retorne APENAS UM ÚNICO OBJETO JSON válido, sem nenhum texto ou formatação adicional.

O objeto JSON deve ter a seguinte estrutura:
{{
    "intent": "A intenção principal do usuário.",
    "location": "A cidade ou local, se mencionado.",
    "date": "A data para previsão do tempo no formato AAAA-MM-DD.",
    "music_title": "O nome da música e/ou artista.",
    "application_name": "O nome do aplicativo a ser aberto.",
    "event_name": "A descrição completa do evento a ser agendado.",
    "event_date": "A data EXATA do evento no formato AAAA-MM-DD.",
    "event_time": "A hora EXATA do evento no formato HH:MM (24 horas)."
}}

Valores possíveis para o campo "intent":
'get_weather', 'get_time', 'exit', 'tocar_musica', 'iniciar_tradutor', 'parar_tradutor', 'open_application', 'schedule_event', 'unknown'.

---
Exemplos de Raciocínio (usando a data de referência acima):

1.  Comando: "marcar reunião de equipe para amanhã às 3 da tarde"
    - Análise: 'amanhã' a partir de {data_hoje.strftime('%Y-%m-%d')} é {(data_hoje + datetime.timedelta(days=1)).strftime('%Y-%m-%d')}. '3 da tarde' é 15:00.
    - JSON esperado: {{"intent": "schedule_event", "event_name": "reunião de equipe", "event_date": "{(data_hoje + datetime.timedelta(days=1)).strftime('%Y-%m-%d')}", "event_time": "15:00"}}

2.  Comando: "agendar consulta com Dr. Silva na próxima sexta-feira às 10h"
    - Análise: A próxima 'sexta-feira' precisa ser calculada. O horário é 10:00.
    - JSON esperado: {{"intent": "schedule_event", "event_name": "consulta com Dr. Silva", "event_date": "2025-10-10", "event_time": "10:00"}}
---

Agora, analise o seguinte comando: "{comando}"
"""
    try:
        resposta = model.generate_content(prompt, request_options={"timeout":15}) # Tempo limite de 15 segundos
        # O .text pode vir com marcações de JSON, então aqui nós limpamos isso.
        json_text = resposta.text.strip().replace("```json", "").replace("```", "")
        import json
        #retorna como dicionario, para facilitar o uso. Podemos pegar o intent por exemplo com resultado['intent']
        return json.loads(json_text)
    except Exception as e:
        if "Deadline exceeded" in str(e):
            print("Erro: A solicitação ao Gemini excedeu o tempo limite.")
            return {"intent": "unknown", "error": "timeout"}
        print("Erro ao analisar comando com Gemini:", e)
        return {"intent": "unknown", "location": None, "date": None, "music_title": None}