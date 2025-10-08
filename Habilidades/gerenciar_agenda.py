import datetime # Data e hora
import os.path
from google.auth.transport.requests import Request # Autenticação e autorização #type: ignore
from google.oauth2.service_account import Credentials # Credenciais de conta de serviço #type: ignore
from googleapiclient.discovery import build # Construção do serviço da API #type: ignore
from googleapiclient.errors import HttpError # Tratamento de erros da API #type: ignore

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials_agenda.json'  # Arquivo de credenciais da conta de serviço
ID_AGENDA = os.getenv("ID_AGENDA") # ID da agenda (pode ser o email do usuário ou o ID da agenda compartilhada)


class GerenciadorAgenda:
    """Inicializa o gerenciador de agenda do Google."""
    def __init__(self):
        self.service = None
        try:
            creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES) # carrega as credenciais.
            self.service = build('calendar', 'v3', credentials=creds) # constrói o serviço da API do Google Calendar.
            print("[INFO] Gerenciador de agenda inicializado com sucesso.")
        except FileNotFoundError:
            print(f"[ERRO] Arquivo de credenciais '{SERVICE_ACCOUNT_FILE}' não encontrado.")
        except Exception as e:
            print(f"[ERRO] Falha ao inicializar o gerenciador de agenda: {e}")

    def adicionar_evento(self, nome_evento, data_evento, hora_evento):
        """Cria um evento na agenda do Google."""
        if not self.service:
            return("[ERRO] Serviço de agenda não inicializado.")

        try:
            # Formata as datas e horas para o padrão ISO 8601
            data_inicio = datetime.datetime.strptime(f"{data_evento} {hora_evento}", "%Y-%m-%d %H:%M") # 
            data_fim = data_inicio + datetime.timedelta(hours=1) #Por padrão cada evento dura 1 hora.
            fuso_horario = 'America/Sao_Paulo'

            #Dicionario com os detalhes do evento:
            evento = {
                'summary': nome_evento,
                'start': {
                    'dateTime': data_inicio.isoformat(),
                    'timeZone': fuso_horario},
                'end': {
                    'dateTime': data_fim.isoformat(),
                    'timeZone': fuso_horario},
                'reminders': {'useDefault': True}, # Usa lembretes padrão do Google Calendar.
            }
            # Usamos a API para inserir o evento na agenda.
            # primary = agenda principal do usuario # evento = dados do evento
            evento_criado = self.service.events().insert(calendarId=ID_AGENDA, body=evento).execute()
            print(f"[INFO] Evento criado: {evento_criado.get('htmlLink')}")
            return f"Evento '{nome_evento} ' adicionado na sua agenda para {data_evento} às {hora_evento}"
        except HttpError as error:
            return f"[ERRO] Ocorreu um erro ao adicionar o evento: {error}"
        except Exception as e:
            return f"[ERRO] Falha ao adicionar o evento: {e}"