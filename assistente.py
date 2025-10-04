#Let's get started#
import os
from funcoes_falar_ouvir import falar, ouvir_comando, escutar_palavra_ativacao
from habilidades import obter_previsao_tempo, analisar_comando_gemini, obter_coordenadas, obter_previsao_futuro

# função principal
def rodar_assistente():
    while True:
        #espera a palavra de ativação
        escutar_palavra_ativacao()
        falar("Sim, estou ouvindo.")
        #Ouve o comando do usuario
        comando = ouvir_comando()

        #processamento do comando
        if not comando:
            continue          

        #Aqui analisamos o comando e pegamos a intenção, cidade e data
        dados = analisar_comando_gemini(comando)
        intent = dados.get("intent")
        #dependendo da intenção que a IA retornar, fazemos algo.
        if intent == 'get_weather':
            cidade = dados.get("location")
            data = dados.get("date")
            if not cidade:
                falar("Por favor, especifique a cidade para a previsão do tempo.")
                continue
            #se a data for hoje ou não especificada, pegamos a previsão atual
            if not data or data == "hoje":
                resposta_clima = obter_previsao_tempo(cidade)
                falar(resposta_clima)
            else:
                #se a data for futura.
                lat, lon = obter_coordenadas(cidade)
                if lat and lon:
                    resposta = obter_previsao_futuro(lat, lon, data)
                    falar(resposta)
                else:
                    falar(f"Desculpe, não achei a cidade {cidade}.")
        elif intent == 'get_time':
            falar("Ainda não sei fazer isso, mas logo aprenderei.")
        elif intent == 'unknown':
            falar("Desculpe, não entendi o comando.")
        elif intent == 'exit':
            falar('Encerrando o assistente. Até mais!')
            break
if __name__ == "__main__":
    rodar_assistente()