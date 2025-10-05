#Let's get started#
import os
import time
from datetime import datetime
from funcoes_falar_ouvir import falar, ouvir_comando, escutar_palavra_ativacao, falar_audio_pre_gravado
from habilidades import obter_previsao_tempo, analisar_comando_gemini, obter_coordenadas, obter_previsao_futuro, pesquisar_musica_youtube
#Multiprocessing para fazer a assistente parecer mais responsiva, sem travar a fala e o ouvir.
from multiprocessing import Process
# controlador para o navegador
from controlador_navegador import ControladorNavegador

# função principal
def rodar_assistente():
    controlador = ControladorNavegador() # inicia o controlador do Navegador fora do if, para evitar reiniciar o navegador toda vez.
    sucesso_ao_iniciar = controlador.iniciar_navegador(navegador='chrome', headless=True) # Inicia o navegador uma vez no começo.
    if not sucesso_ao_iniciar:
        print("Não foi possível iniciar o navegador. A funcionalidade de tocar música estará indisponível.")
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
                video_id = pesquisar_musica_youtube(titulo_musica)
                if video_id:
                    #monta a URL completa do vídeo
                    url_video = f"https://www.youtube.com/watch?v={video_id}"
                    #manda o navegador abrir o vídeo pela URL
                    controlador.tocar_musica(url_video)
                    resposta_final = f"Tocando {titulo_musica} no YouTube."
                else:
                    resposta_final = "Não consegui encontrar a música no YouTube."
            else:
                resposta_final = "Não consegui identificar o título da música."
        elif intent == 'unknown':
            falar("Desculpe, não entendi o comando.")
        elif intent == 'exit':
            controlador.fechar_navegador() # Fecha o navegador ao sair
            falar('Encerrando o assistente. Até mais!')
            break


if __name__ == "__main__":
    rodar_assistente()