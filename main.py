#Let's get started#

import speech_recognition as sr
from gtts import gTTS
import os
import playsound

# função para converter texto em fala
def falar(texto):
    try:
        tts = gTTS(text=texto, lang='pt-br')
        arquivo_audio = 'fala.mp3'
        tts.save(arquivo_audio)
        playsound.playsound(arquivo_audio)
        os.remove(arquivo_audio)
    except Exception as e:
        print(f"Erro ao tentar falar: {e}")
# função para ouvir e reconhecer fala
def ouvir_comando():
    reconhecedor = sr.Recognizer()
    # Usando o microfone padrão do sistema
    with sr.Microphone() as source:
        print("Ajustando ruído de ambiente...")
        # ajuste para ruído de ambiente
        reconhecedor.adjust_for_ambient_noise(source, duration=1)
        print("Ouvindo...")
        #Gravando o que o usuario fala
        fala = reconhecedor.listen(source)
        try:
            print("Reconhecendo...")
            #reconhecendo a fala em pt-br
            comando = reconhecedor.recognize_google(fala, language='pt-BR')
            print(f"Você disse: {comando}\n")
            return comando.lower()
        
        except sr.UnknownValueError:
            #caso não entenda o que foi dito
            print("Desculpe, pode repetir?")
            return None
        except sr.RequestError as e:
            print(f"Erro ao conectar ao serviço de reconhecimento de fala: {e}")
            return None
# função principal
def rodar_assistente():
    falar("Olá! Sou sua assistente virtual. Como posso ajudar?")
    while True:
        comando = ouvir_comando()
        #por enquanto ele só repede e para se ouvir "sair"
        if comando:
            falar(f"Você disse: {comando}")
            if "sair" in comando:
                falar("Encerrando a assistente. Até mais!")
                break
if __name__ == "__main__":
    rodar_assistente()