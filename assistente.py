# ==========================================================
# 1. Módulos da Biblioteca Padrão do Python
# ==========================================================
import os
import time
from datetime import datetime
from multiprocessing import Process # Para executar tarefas em paralelo (ex: falar enquanto ouve).
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
                         pesquisar_musica_youtube)
# Importa a classe para controlar o volume do sistema.
from controle_volume import ControladorVolume
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
        if not self.navegador_iniciado:
            print("Não foi possível iniciar o navegador. A funcionalidade de tocar música estará indisponível.")
        
    def _processar_comando(self, comando):
        """Processa o comando e executa a ação apropriada."""
        if not comando: # Se não entendeu, volta para o começo.
            return
        processo_feedback = Process(target=falar_audio_pre_gravado, args=("processando",)) # assistente responde em um processo separado
        processo_feedback.start()

        dados = analisar_comando_gemini(comando) #Aqui analisamos o comando e pegamos a intenção, cidade e data
        intent = dados.get("intent")
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        resposta_final = "" 

        #Lógica de decisão baseada na intenção
        ### CLIMA
        if intent == 'get_weather':
            cidade = dados.get("location")
            data = dados.get("date") # Formato: '2025-10-04'
            if not cidade: #Se não tiver cidade, volta para o começo.
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
            processo_feedback.join() #espera o processo de feedback terminar
            falar(resposta_final)

        ### TOCAR MÚSICA
        elif intent == 'tocar_musica':
            titulo_musica = dados.get("music_title")
            if titulo_musica and self.navegador_iniciado: # Se o navegador iniciou com sucesso
                video_id = pesquisar_musica_youtube(titulo_musica)
                if video_id:
                    #monta a URL completa do vídeo
                    url_video = f"https://www.youtube.com/watch?v={video_id}"
                    #manda o navegador abrir o vídeo pela URL
                    self.controlador_web.tocar_musica(url_video)
                    resposta_final = f"Tocando {titulo_musica} no YouTube."
                else:
                    resposta_final = "Não consegui encontrar a música no YouTube."
                falar(resposta_final)
        ### TRADUTOR
        elif intent == 'iniciar_tradutor':
            resposta_final = self.iniciar_tradutor()
            processo_feedback.join() #espera o processo de feedback terminar
            falar(resposta_final)
        elif intent == 'parar_tradutor':
            resposta_final = self._parar_tradutor()
            processo_feedback.join() #espera o processo de feedback terminar
            falar(resposta_final)
        elif intent == 'exit':
            return False # Sinaliza para sair
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
                self.controlador_som.definir_volume(0.2) # Abaixa o volume do sistema para ouvir melhor o comando
                processo_fala = Process(target=falar_audio_pre_gravado, args=("ouvindo",)) # assistente responde em um processo separado
                processo_fala.start()
                time.sleep(1.0) #pausa para evitar que o assistente se ouça
                comando = ouvir_comando() #Ouve o comando do usuario
                continuar_execucao = self._processar_comando(comando)
                if not continuar_execucao:
                    self.desligar()
                    break
            finally:
                self.controlador_som.restaurar_volume() # Restaura o volume original do sistema
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