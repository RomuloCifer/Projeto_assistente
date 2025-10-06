# ==========================================================
# 1. Módulos da Biblioteca Padrão do Python
# ==========================================================
import os
import time
from datetime import datetime
from multiprocessing import Process # Para executar tarefas em paralelo (ex: falar enquanto ouve).

# ==========================================================
# 3. Módulos Locais (Nossos próprios arquivos .py)
# ==========================================================
# Importa a classe para controlar o navegador (Opera/Chrome) para tocar músicas.
from controlador_navegador import ControladorNavegador
# Importa funções básicas de fala e escuta.
from funcoes_falar_ouvir import falar, ouvir_comando, falar_audio_pre_gravado
# Importa as habilidades principais do assistente (clima, análise de comando, busca de música).
from habilidades import (obter_previsao_tempo, analisar_comando_gemini,
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



# função principal
def rodar_assistente():
    controlador_web = ControladorNavegador() # inicia o controlador do Navegador fora do if, para evitar reiniciar o navegador toda vez.
    controlador_som = ControladorVolume() # Controlador de volume
    detector_wake_word = DetectorPalavraDeAtivacao(PORCUPINE_ACCESS_KEY, palavra_chave="alexa") # Inicializa o detector de palavra de ativação

    sucesso_navegador = controlador_web.iniciar_navegador(navegador='chrome', headless=True) # Inicia o navegador uma vez no começo.
    if not sucesso_navegador:
        print("Não foi possível iniciar o navegador. A funcionalidade de tocar música estará indisponível.")
    while True:
        detector_wake_word.iniciar_escuta() #espera a palavra de ativação
        try:
            controlador_som.definir_volume(0.2) # Abaixa o volume do sistema para ouvir melhor o comando
            processo_fala = Process(target=falar_audio_pre_gravado, args=("ouvindo",)) # assistente responde em um processo separado
            processo_fala.start()
            time.sleep(1.1) #pausa para evitar que o assistente se ouça
            comando = ouvir_comando() #Ouve o comando do usuario
            #Se não entendeu, volta para o começo.
            if not comando:
                continue
            
            #Se entender algum comando, antes de analisar, fala que está processando. Evita o silêncio constrangedor.
            processo_feedback = Process(target=falar_audio_pre_gravado, args=("processando",))
            processo_feedback.start()
            #Aqui analisamos o comando e pegamos a intenção, cidade e data
            dados = analisar_comando_gemini(comando)
            intent = dados.get("intent")
            data_hoje = datetime.now().strftime('%Y-%m-%d')


            #dependendo da intenção que a IA retornar, fazemos algo.
            if intent == 'get_weather':
                cidade = dados.get("location")
                data = dados.get("date") # Formato: '2025-10-04'
                #Se não tiver cidade, volta para o começo.
                if not cidade:
                    continue       
                resposta_final = ""     
                #se a data for hoje ou não especificada, pegamos a previsão atual
                if not data or data == data_hoje:
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
            #caso a intenção seja tocar musica.
            elif intent == 'tocar_musica':
                titulo_musica = dados.get("music_title")
                if titulo_musica:
                    video_id = pesquisar_musica_youtube(titulo_musica)
                    if video_id:
                        #monta a URL completa do vídeo
                        url_video = f"https://www.youtube.com/watch?v={video_id}"
                        #manda o navegador abrir o vídeo pela URL
                        controlador_web.tocar_musica(url_video)
                        resposta_final = f"Tocando {titulo_musica} no YouTube."
                    else:
                        resposta_final = "Não consegui encontrar a música no YouTube."
                else:
                    resposta_final = "Não consegui identificar o título da música."
            elif intent == 'unknown':
                falar("Desculpe, não entendi o comando.")
            elif intent == 'exit':
                controlador_web.fechar_navegador() # Fecha o navegador ao sair
                detector_wake_word.fechar() # Para o detector de palavra de ativação
                falar('Encerrando o assistente. Até mais!')
                break
        finally:
            controlador_som.restaurar_volume() # Restaura o volume original do sistema


if __name__ == "__main__":
    rodar_assistente()