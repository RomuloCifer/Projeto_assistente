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
            #lista de palavras para pegar a cidade            
            palavras_gatilho = ['em', 'de', 'para', 'na', 'no']
            palavras = comando.split()
            try:
                #tenta pegar o indice da palavra gatilho
                indice_gatilho = next(i for i, palavra in enumerate(palavras) if palavra in palavras_gatilho)
                #pega tudo que vem depois do gatilho como nome da cidade
                cidade = ' '.join(palavras[indice_gatilho + 1:])
                #se não entender a cidade, pede para repetir
                if not cidade:
                    falar("Desculpe, não entendi a cidade")
                    continue        
                resposta_clima = obter_previsao_tempo(cidade)
                falar(resposta_clima)   
            #se não encontrar nenhuma palavra gatilho
            except StopIteration:
                falar("Não ouvi gatilhos")

        else:
            falar(f"entendi o comando, mas ainda não sei executar")
if __name__ == "__main__":
    rodar_assistente()