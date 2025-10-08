# ==========================================================
# 1. Módulos da Biblioteca Padrão do Python
# ==========================================================
import os
import time
from datetime import datetime
from multiprocessing import Process # Para executar tarefas em paralelo (ex: falar enquanto ouve).

# ==========================================================
# 2. Módulos Locais (Nossos próprios arquivos .py e pastas de Habilidades)
# ==========================================================
# Importa a classe para controlar o navegador (Opera/Chrome) para tocar músicas.
from controlador_navegador import ControladorNavegador
# Importa funções básicas de fala e escuta.
from funcoes_falar_ouvir import falar, ouvir_comando, falar_audio_pre_gravado
# Importa as habilidades principais do assistente (clima, análise de comando, busca de música).
# E as classes GerenciadorAgenda.
from Habilidades import (obter_previsao_tempo, analisar_comando_gemini,
                         obter_coordenadas, obter_previsao_futuro,
                         pesquisar_musica_youtube, obter_data_hora_atual, GerenciadorAgenda)
# Importa a classe TradutorClipboard do seu próprio módulo tradutor_clipboard.py
from tradutor_clipboard import TradutorClipboard, iniciar_monitoramento


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
        
        # Cria uma instância da classe TradutorClipboard.
        self.tradutor_clipboard_instance = TradutorClipboard() 
        # Esta variável guardará a referência ao processo (multiprocessing) do tradutor.
        self.processo_tradutor = None 
        
        self.gerenciador_agenda = GerenciadorAgenda() # Inicializa o gerenciador de agenda
        if not self.navegador_iniciado:
            print("Não foi possível iniciar o navegador. A funcionalidade de tocar música estará indisponível.")
        
        # Cada chave (string da intenção) aponta para um método da própria classe que vai tratar essa intenção.
        self.handlers = {
            'get_weather': self._handle_get_weather,
            'tocar_musica': self._handle_tocar_musica,
            'iniciar_tradutor': self._handle_iniciar_tradutor,
            'parar_tradutor': self._handle_parar_tradutor,
            'get_time': self._handle_get_time,
            'schedule_event': self._handle_schedule_event,
            'exit': self._handle_exit
            # Exemplo de como adicionar uma nova habilidade:
            # 'open_application': self._handle_open_application,
        }

    # ==========================================================
    # Cada método abaixo contém a lógica de um antigo bloco "elif" e é responsável por sua resposta final.
    # ==========================================================

    def _handle_get_weather(self, dados, processo_feedback):
        """Trata da intenção de obter a previsão do tempo."""
        cidade = dados.get("location")
        data = dados.get("date") # Formato: '2025-10-04'
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        resposta_final = ""
        
        if not cidade: #Se não tiver cidade, volta para o começo.
            processo_feedback.join()
            falar("Por favor, diga a cidade para a previsão do tempo.")
            return True      
        
        if not data or data == data_hoje: #se a data for hoje ou não especificada, pegamos a previsão atual
            resposta_final = obter_previsao_tempo(cidade)
        else:
            #se a data for futura.
            lat, lon = obter_coordenadas(cidade)
            if lat and lon:
                resposta_final = obter_previsao_futuro(lat, lon, data)
            else:
                resposta_final = f"Desculpe, não consegui obter a previsão do tempo."
        
        processo_feedback.join() # Espera o áudio de "processando" terminar
        falar(resposta_final) # Fala a resposta final
        return True # Sinaliza para continuar o loop principal do assistente

    def _handle_tocar_musica(self, dados, processo_feedback):
        """Trata da intenção de tocar música."""
        titulo_musica = dados.get("music_title")
        resposta_final = ""
        
        # Verifica se temos um título e se o navegador está pronto
        if titulo_musica and self.navegador_iniciado:
            video_id = pesquisar_musica_youtube(titulo_musica)
            # Verifica se a busca no YouTube teve sucesso
            if video_id:
                url_video = f"https://www.youtube.com/watch?v={video_id}"
                self.controlador_web.tocar_musica(url_video)
                resposta_final = f"Tocando {titulo_musica} no YouTube."
            else:
                # A busca falhou, então informamos o usuário
                resposta_final = "Não consegui encontrar a música no YouTube."
        else:
            # O comando não tinha um título ou o navegador falhou
            resposta_final = "Não consegui identificar a música ou o navegador não foi iniciado."

        processo_feedback.join() # Espera o áudio de "processando" terminar
        falar(resposta_final) # Fala a resposta final
        return True # Sinaliza para continuar o loop principal do assistente

    def _handle_iniciar_tradutor(self, _, processo_feedback): # Usamos '_' para indicar que 'dados' não é utilizado neste handler.
        """Trata da intenção de iniciar o tradutor."""
        resposta_final = self.iniciar_tradutor() 
        processo_feedback.join() # Espera o áudio de "processando" terminar
        falar(resposta_final) # Fala a resposta final
        return True # Sinaliza para continuar o loop principal do assistente

    def _handle_parar_tradutor(self, _, processo_feedback): # Usamos '_' para indicar que 'dados' não é utilizado neste handler.
        """Trata da intenção de parar o tradutor."""
        resposta_final = self._parar_tradutor()
        processo_feedback.join() # Espera o áudio de "processando" terminar
        falar(resposta_final) # Fala a resposta final
        return True # Sinaliza para continuar o loop principal do assistente

    def _handle_get_time(self, _, processo_feedback): # Usamos '_' para indicar que 'dados' não é utilizado neste handler.
        """Trata da intenção de obter a data e hora."""
        resposta_final = obter_data_hora_atual() 
        processo_feedback.join() # Espera o áudio de "processando" terminar
        falar(resposta_final) # Fala a resposta final
        return True # Sinaliza para continuar o loop principal do assistente

    def _handle_schedule_event(self, dados, processo_feedback):
        """Trata da intenção de agendar um evento."""
        nome_evento = dados.get("event_name")
        data_evento = dados.get("event_date")
        hora_evento = dados.get("event_time")
        resposta_final = ""

        if nome_evento and data_evento and hora_evento: # Se todas as informações estiverem presentes
            resposta_final = self.gerenciador_agenda.adicionar_evento(nome_evento, data_evento, hora_evento) # Tenta adicionar o evento
        else:
            resposta_final = "Informações do evento incompletas. Preciso do nome, data e hora." # Informa que faltam dados
        
        processo_feedback.join() # Espera o áudio de "processando" terminar
        falar(resposta_final) # Fala a resposta final
        return True # Sinaliza para continuar o loop principal do assistente

    def _handle_exit(self, _, processo_feedback): # Usamos '_' para indicar que 'dados' não é utilizado neste handler.
        """Trata da intenção de encerrar o assistente."""
        processo_feedback.join() # Garante que o som de "processando" termine
        return False # Sinaliza para o loop principal do assistente que ele deve parar

    # ==========================================================
    # MÉTODO _processar_comando - Handlers!
    # ==========================================================

    def _processar_comando(self, comando):
        """
        Processa o comando, analisa a intenção e executa o handler correspondente.
        Este método atua como o 'gerente' que delega a tarefa ao handler correto.
        """
        if not comando: # Se não entendeu o comando de voz, retorna para continuar ouvindo.
            return True
        
        # Inicia um processo separado para tocar o áudio de feedback "processando".
        processo_feedback = Process(target=falar_audio_pre_gravado, args=("processando",)) 
        processo_feedback.start()

        # Envia o comando para o Gemini analisar e extrair a intenção e os dados.
        dados = analisar_comando_gemini(comando) 

        # TRATAMENTO DE ERRO: Se a comunicação com o Gemini falhou ou excedeu o tempo limite.
        if dados.get("error") == "timeout":
            resposta_final = "Não consegui me conectar ao meu cérebro a tempo. Pode ser um problema de rede. Tente de novo, por favor."
            processo_feedback.join() # Espera o áudio de "processando" terminar.
            falar(resposta_final) # Fala a mensagem de erro.
            return True # Sinaliza para continuar a execução do assistente.

        intent = dados.get("intent") # Pega a intenção identificada pelo Gemini.

        # Tenta encontrar o método de tratamento (handler) correspondente à intenção no dicionário 'self.handlers'.
        handler = self.handlers.get(intent)

        if handler:
            # Se um handler para a intenção foi encontrado, ele é executado.
            # O handler é responsável por finalizar o 'processo_feedback' e falar a 'resposta_final'.
            return handler(dados, processo_feedback)
        else:
            # Se a intenção não estiver mapeada no dicionário ou for 'unknown'.
            resposta_final = "Desculpe, não entendi o que você pediu."
            processo_feedback.join() # Espera o áudio de "processando" terminar.
            falar(resposta_final) # Fala a resposta padrão.
            return True # Sinaliza para continuar a execução do assistente

    # ==========================================================
    # MÉTODOS DE GERENCIAMENTO DE RECURSOS (Tradutor, Desligar, etc.)
    # ==========================================================

    def iniciar_tradutor(self): # Seu nome original para iniciar o tradutor
        """
        Inicia o monitoramento do clipboard em um processo separado.
        Cria um novo processo que executa o método 'iniciar_tradutor()' da instância de TradutorClipboard.
        """
        # Verifica se o processo do tradutor já está ativo.
        if self.processo_tradutor and self.processo_tradutor.is_alive():
            return "O modo de tradução já está ativo."
        
        # Cria um novo processo para executar o método 'iniciar_tradutor' da nossa instância de TradutorClipboard.
        self.processo_tradutor = Process(target=iniciar_monitoramento) # 
        self.processo_tradutor.start() # Inicia o processo.
        return "Modo de tradução ativado."
    
    def _parar_tradutor(self): # Seu nome original para parar o tradutor
        """
        Para o monitoramento do clipboard, encerrando o processo do tradutor.
        """
        # Verifica se o processo do tradutor existe e está ativo.
        if self.processo_tradutor and self.processo_tradutor.is_alive():
            self.processo_tradutor.terminate() # Encerra o processo do tradutor "à força".
            self.processo_tradutor.join() # Espera o processo terminar completamente.
            return "Modo de tradução desativado."
        return "O modo de tradução não está ativo." # Se não estava ativo, informa.

    def executar(self):
        """
        Loop principal do assistente. Fica aguardando a palavra de ativação e processa comandos.
        """
        while True:
            self.detector_wake_word.iniciar_escuta() #espera a palavra de ativação
            try:
                # Abaixa o volume dos outros aplicativos para ouvir melhor o comando do usuário.
                self.controlador_som.definir_volume_aplicativos(0.2, processos_ignorar=['python.exe', 'py.exe']) 
                
                # Inicia um processo para tocar o áudio de feedback "ouvindo".
                processo_fala = Process(target=falar_audio_pre_gravado, args=("ouvindo",)) 
                processo_fala.start()
                
                time.sleep(1.0) # Pequena pausa para evitar que o assistente capte sua própria fala.
                comando = ouvir_comando() # Ouve o comando de voz do usuário.
                
                # Processa o comando. O método _processar_comando decide se continua ou encerra.
                continuar_execucao = self._processar_comando(comando)
                
                if not continuar_execucao: # Se o comando sinalizou para encerrar (ex: "Alexa, sair").
                    self.desligar() # Executa a rotina de desligamento.
                    break # Sai do loop principal.
            finally:
                # Garante que o volume dos aplicativos seja restaurado, mesmo se houver um erro.
                self.controlador_som.restaurar_volume_aplicativos() 

    def desligar(self):
        """
        Desliga o assistente, fechando todos os recursos abertos de forma segura.
        """
        if self.navegador_iniciado:
            self.controlador_web.fechar_navegador() # Fecha o navegador se estiver aberto.
        self.detector_wake_word.fechar() # Desativa o detector de palavra de ativação.
        self._parar_tradutor() # Garante que o tradutor seja parado.
        falar('Encerrando o assistente. Até mais!') # Mensagem final de despedida.

if __name__ == "__main__":
    # Ponto de entrada principal do script.
    assistente = Assistente(palavra_ativacao="alexa") # Cria uma instância do Assistente.
    assistente.executar() # Inicia o loop de execução do assistente.