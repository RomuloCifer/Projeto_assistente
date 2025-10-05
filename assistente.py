#Let's get started#
import os
import time
from datetime import datetime
from funcoes_falar_ouvir import falar, ouvir_comando, escutar_palavra_ativacao, falar_audio_pre_gravado
from habilidades import obter_previsao_tempo, analisar_comando_gemini, obter_coordenadas, obter_previsao_futuro
#Multiprocessing para fazer a assistente parecer mais responsiva, sem travar a fala e o ouvir.
from multiprocessing import Process
# controlador para o navegador
from controlador_navegador import ControladorNavegador

# função principal
def rodar_assistente():
    while True:
        #espera a palavra de ativação
        escutar_palavra_ativacao()
        #Aqui a assistente vai falar que está ouvindo, em um processo separado para não travar o ouvir.
        processo_fala = Process(target=falar_audio_pre_gravado, args=("ouvindo",))
        processo_fala.start()
        #pausa para evitar que o assistente se ouça
        time.sleep(1.1)
        #Ouve o comando do usuario
        comando = ouvir_comando()
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
                processo.feedback.join() #espera o processo de feedback terminar
                falar(f"Tocando {titulo_musica}")
                controlador = ControladorNavegador()
                sucesso = controlador.iniciar_navegador(navegador='chrome', headless=False)
                #se conseguir iniciar o navegador, toca a música.
                if sucesso:
                    controlador.tocar_musica(titulo_musica)
                else:
                    processo.feedback.join() #espera o processo de feedback terminar
                    falar("Não consegui iniciar o navegador para tocar a música.")
            #Caso não tenha entendido o título da música.
            else:
                processo.feedback.join() #espera o processo de feedback terminar
                falar("Não consegui identificar o título da música.")
        elif intent == 'unknown':
            falar("Desculpe, não entendi o comando.")
        elif intent == 'exit':
            falar('Encerrando o assistente. Até mais!')
            break


if __name__ == "__main__":
    rodar_assistente()