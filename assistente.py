#Let's get started#
import os
from funcoes_falar_ouvir import falar, ouvir_comando, escutar_palavra_ativacao
from habilidades import obter_previsao_tempo




# função principal
def rodar_assistente():
    while True:
        #espera a palavra de ativação
        escutar_palavra_ativacao()
        falar("Sim, estou ouvindo.")
        comando = ouvir_comando()
        #processamento do comando
        if not comando:
            continue            
        if "sair" in comando:
            falar("Encerrando a assistente. Até mais!")
            break
        elif "que horas são" in comando:
            falar("Ainda não sei ver as horas, mas estou aprendendo!")
        elif any(kw in comando for kw in ["previsao", "tempo", "clima"]):
            falar(obter_previsao_tempo())
        else:
            falar(f"entendi o comando, mas ainda não sei executar")
if __name__ == "__main__":
    rodar_assistente()