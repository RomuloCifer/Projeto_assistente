#Let's get started#
import os
from datetime import datetime
from funcoes_falar_ouvir import falar, ouvir_comando, escutar_palavra_ativacao
from habilidades import obter_previsao_tempo, analisar_comando_gemini, obter_coordenadas, obter_previsao_futuro
#Multiprocessing para fazer a assistente parecer mais responsiva, sem travar a fala e o ouvir.
from multiprocessing import Process

# função principal
def rodar_assistente():
    while True:
        #espera a palavra de ativação
        escutar_palavra_ativacao()
        #Aqui a assistente vai falar que está ouvindo, em um processo separado para não travar o ouvir.
        processo_fala = Process(target=falar, args=("Sim?",))
        processo_fala.start()
        #Ouve o comando do usuario
        comando = ouvir_comando()

        #processamento do comando
        if not comando:
            continue          

        #Aqui analisamos o comando e pegamos a intenção, cidade e data
        dados = analisar_comando_gemini(comando)
        intent = dados.get("intent")
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        #dependendo da intenção que a IA retornar, fazemos algo.
        if intent == 'get_weather':
            cidade = dados.get("location")
            data = dados.get("date") # Formato: '2025-10-04'
            if not cidade:
                continue
            #se a data for hoje ou não especificada, pegamos a previsão atual
            if not data or data == data_hoje:
                processo_fala_dia = Process(target=falar, args=(f"Só um momento...",))
                processo_fala_dia.start()
                resposta_clima = obter_previsao_tempo(cidade)
                processo_fala_dia.join() # espera a fala terminar antes de continuar
                falar(resposta_clima)
            else:
                try:
                    data_obj = datetime.strptime(data, '%Y-%m-%d')
                    dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
                    dia_da_semana = dias[data_obj.weekday()]
                    texto_feedback = f"Ok, {cidade}, {dia_da_semana}..."
                except ValueError:
                    texto_feedback = f"Ok, {cidade}, na data {data}..."
                processo_fala_futura = Process(target=falar, args=(texto_feedback,))
                processo_fala_futura.start()
                #se a data for futura.
                lat, lon = obter_coordenadas(cidade)
                if lat and lon:
                    resposta = obter_previsao_futuro(lat, lon, data)
                    processo_fala_futura.join() #esperar terminar...
                    falar(f"Em {cidade}, {resposta}")
                else:
                    processo_fala_futura.join() #esperar terminar...
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