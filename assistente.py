# ==========================================================
# 1. Módulos da Biblioteca Padrão do Python
# ==========================================================
import os
import time
from datetime import datetime
from multiprocessing import Process # Para executar tarefas em paralelo (ex: falar enquanto ouve).
from Habilidades.data_hora import obter_data_hora_atual
from tradutor_clipboard import monitorar_clipboard

# ==========================================================
# 3. Módulos Locais (Nossos próprios arquivos .py)
# ==========================================================
# Importa a classe para controlar o navegador (Opera/Chrome) para tocar músicas.
from controlador_navegador import ControladorNavegador
# Importa funções básicas de fala e escuta.
from funcoes_falar_ouvir import falar, ouvir_comando, falar_audio_pre_gravado
# Importa as habilidades principais do assistente (clima, análise de comando, busca de música).
from Habilidades import (obter_previsao_tempo, analisar_comando_gemini,
                         obter_coordenadas, obter_previsao_futuro,
                         pesquisar_musica_youtube, obter_data_hora_atual, GerenciadorAgenda)
# Importa a classe para controlar o volume do sistema.
from controle_volume_updated import ControladorVolume
# Importa a nova classe que detecta a palavra de ativação.
from palavra_ativacao import DetectorPalavraDeAtivacao

# Carrega as variáveis de ambiente (como as chaves de API) uma única vez.
from dotenv import load_dotenv # type: ignore
load_dotenv()
# Pega a chave do Porcupine do arquivo .env.
PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY")



# classe principal
class Assistente:
    def __init__(self, palavra_ativacao="alexa", navegador='chrome', headless=False, sensibilidade=0.5):
        self.controlador_web = ControladorNavegador() # inicia o controlador do Navegador
        self.controlador_som = ControladorVolume() # Controlador de volume
        self.detector_wake_word = DetectorPalavraDeAtivacao(PORCUPINE_ACCESS_KEY, palavra_chave=palavra_ativacao, sensitivity=sensibilidade) # Inicializa o detector de palavra de ativação
        self.navegador_iniciado = self.controlador_web.iniciar_navegador(navegador=navegador, headless=headless) # Inicia o navegador uma vez no começo.
        self.processo_tradutor = None # Processo do tradutor clipboard
        self.gerenciador_agenda = GerenciadorAgenda() # Inicializa o gerenciador de agenda
        if not self.navegador_iniciado:
            print("Não foi possível iniciar o navegador. A funcionalidade de tocar música estará indisponível.")
        
    def _processar_comando(self, comando):
        """Processa o comando e executa a ação apropriada."""
        if not comando: # Se não entendeu, volta para o começo.
            return
        processo_feedback = Process(target=falar_audio_pre_gravado, args=("processando",))
        processo_feedback.start()

        dados = analisar_comando_gemini(comando) #Aqui analisamos o comando e pegamos a intenção, cidade e data

        # TRATAMENTO DE ERRO: Se o Gemini falhou ou deu timeout
        if dados.get("error") == "timeout":
            resposta_final = "Não consegui me conectar ao meu cérebro a tempo. Pode ser um problema de rede. Tente de novo, por favor."
            processo_feedback.join()
            falar(resposta_final)
            return True # Continua a execução, volta a ouvir

        intent = dados.get("intent")
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        resposta_final = "" 

        #Lógica de decisão baseada na intenção
        ### CLIMA
        if intent == 'get_weather':
            cidade = dados.get("location")
            data = dados.get("date") # Formato: '2025-10-04'
            if not cidade: #Se não tiver cidade, volta para o começo.
                processo_feedback.join()
                falar("Por favor, diga a cidade para a previsão do tempo.")
                return       
            if not data or data == data_hoje: #se a data for hoje ou não especificada, pegamos a previsão atual
                resposta_final = obter_previsao_tempo(cidade)
            else:
                #se a data for futura.
                lat, lon = obter_coordenadas(cidade)
                if lat and lon:
                    resposta_final = obter_previsao_futuro(lat, lon, data)
                else:
                    resposta_final = f"Desculpe, não consegui obter a previsão do tempo."
            processo_feedback.join()
            falar(resposta_final)

        ### TOCAR MÚSICA
        elif intent == 'tocar_musica':
            titulo_musica = dados.get("music_title")

            # Verifica se temos um título e se o navegador está pronto
            if titulo_musica and self.navegador_iniciado:
                video_id = pesquisar_musica_youtube(titulo_musica)

                # Verifica se a busca no YouTube teve sucesso
                if video_id:
                    url_video = f"https://www.youtube.com/watch?v={video_id}"
                    self.controlador_web.tocar_musica(url_video)
                    resposta_final = f"Tocando {titulo_musica} no YouTube."
                    falar(resposta_final)
                else:
                    # A busca falhou, então informamos o usuário
                    resposta_final = "Não consegui encontrar a música no YouTube."
                    falar(resposta_final)
            else:
                # O comando não tinha um título ou o navegador falhou
                resposta_final = "Não consegui identificar a música ou o navegador não foi iniciado."
                falar(resposta_final)
        ### TRADUTOR
        elif intent == 'iniciar_tradutor':
            resposta_final = self.iniciar_tradutor()
            processo_feedback.join()
            falar(resposta_final)
        elif intent == 'parar_tradutor':
            resposta_final = self._parar_tradutor()
            processo_feedback.join()
            falar(resposta_final)
        elif intent == 'exit':
            return False # Sinaliza para sair
                
        ### DATA E HORA
        elif intent == 'get_time':
            resposta_final = obter_data_hora_atual()
            falar(resposta_final)
    
        ### AGENDA
        elif intent == "schedule_event":
            nome_evento = dados.get("event_name")
            data_evento = dados.get("event_date")
            hora_evento = dados.get("event_time")

            if nome_evento and data_evento and hora_evento:
                resposta_final = self.gerenciador_agenda.adicionar_evento(nome_evento, data_evento, hora_evento)
            else:
                resposta_final = "Informações do evento incompletas. Preciso do nome, data e hora."
            
            processo_feedback.join()
            falar(resposta_final)
        else:
            # Caso a intenção seja 'unknown' ou não esteja listada
            resposta_final = "Desculpe, não entendi o que você pediu."
            processo_feedback.join()
            falar(resposta_final)

        return True # Continua a execução do assistente

    def iniciar_tradutor(self):
        """Inicia o monitoramento do clipboard em um processo separado."""
        if self.processo_tradutor and self.processo_tradutor.is_alive():
            return "O modo de tradução já está ativo."

        self.processo_tradutor = Process(target=monitorar_clipboard)
        self.processo_tradutor.start()
        return "Modo de tradução ativado."
    
    def _parar_tradutor(self):
        """Para o monitoramento do clipboard."""
        if self.processo_tradutor and self.processo_tradutor.is_alive():
            self.processo_tradutor.terminate()
            self.processo_tradutor.join()
            return "Modo de tradução desativado."
        return "O modo de tradução não está ativo."
    def executar(self):
        """Loop principal do assistente."""
        while True:
            self.detector_wake_word.iniciar_escuta() #espera a palavra de ativação
            try:
                self.controlador_som.definir_volume_aplicativos(0.2, processos_ignorar=['python.exe', 'py.exe']) # Abaixa o volume dos apps com som (exceto python.exe)
                processo_fala = Process(target=falar_audio_pre_gravado, args=("ouvindo",)) # assistente responde em um processo separado
                processo_fala.start()
                time.sleep(1.0) #pausa para evitar que o assistente se ouça
                comando = ouvir_comando() #Ouve o comando do usuario
                continuar_execucao = self._processar_comando(comando)
                if not continuar_execucao:
                    self.desligar()
                    break
            finally:
                self.controlador_som.restaurar_volume_aplicativos() # Restaura o volume original dos apps
    def desligar(self):
        """Desliga o assistente, fechando recursos."""
        if self.navegador_iniciado:
            self.controlador_web.fechar_navegador() # Fecha o navegador ao sair
        self.detector_wake_word.fechar() # Para o detector de palavra de ativação
        self._parar_tradutor() # Para o tradutor se estiver ativo
        falar('Encerrando o assistente. Até mais!')



if __name__ == "__main__":
    assistente = Assistente(palavra_ativacao="alexa")
    assistente.executar()