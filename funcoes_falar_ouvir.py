import speech_recognition as sr # type: ignore
from gtts import gTTS # type: ignore
import playsound, pvporcupine, pyaudio # type: ignore
import os
# porcupine espera áudio em 16-bit, por isso importamos o struct
import struct

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
    # Só para de ouvir quando a pausa for de 1.5 segundos
    reconhecedor.pause_threshold = 2
    # Usando o microfone padrão do sistema
    with sr.Microphone() as source:
        print("Ajustando ruído de ambiente...")
        # ajuste para ruído de ambiente
        reconhecedor.adjust_for_ambient_noise(source, duration=1)
        print("Ouvindo...")
        reconhecedor.energy_threshold = 600  # Ajusta o limiar de energia para filtrar ruídos baixos
        #Gravando o que o usuario fala
        fala = reconhecedor.listen(source, phrase_time_limit=7)
        try:
            print("Reconhecendo...")
            #reconhecendo a fala em pt-br
            comando = reconhecedor.recognize_google(fala, language='pt-BR') #type: ignore
            print(f"Você disse: {comando}\n")
            return comando.lower()
        
        except sr.UnknownValueError:
            #caso não entenda o que foi dito
            print("Desculpe, pode repetir?")
            return None
        except sr.RequestError as e:
            print(f"Erro ao conectar ao serviço de reconhecimento de fala: {e}")
            return None
        
def falar_audio_pre_gravado(nome_arquivo):
    """Função para tocar um áudio pré-gravado."""
    try:
        caminho_audio = os.path.join("audios", f"{nome_arquivo}.mp3")
        playsound.playsound(caminho_audio)
    except Exception as e:
        #Se o arquivo não existir ou der erro ao tocar.
        print(f"Erro ao tentar tocar o áudio '{nome_arquivo}': {e}")