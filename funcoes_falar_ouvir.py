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
        
# função para escutar a palavra de ativação
def escutar_palavra_ativacao():
    from dotenv import load_dotenv # type: ignore
    #carregar a keys do .env
    load_dotenv()
    #ACCESS PORCUPINE
    ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY")
    if not ACCESS_KEY:
        raise ValueError("Chave de API do Porcupine não encontrada. Verifique seu arquivo .env")
    ######################################

    palavra_chave = "alexa"
    print(f"Esperando pela palavra de ativação {palavra_chave}")
    porcupine = None
    pa = None
    audio_stream = None

    try:
        #inicia a IA para captar a palavra chave
        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keywords=[palavra_chave]
        )
        #pyaudio para o microfone principal
        pa = pyaudio.PyAudio()
        #fluxo de audio
        audio_stream = pa.open(
            #a taxa que o porcupine espera o audio
            rate=porcupine.sample_rate,
            #audio mono
            channels=1,
            #formato de audio numeros int de 16bits
            format=pyaudio.paInt16,
            #somente capturar entrada, não saida
            input=True,
            #ler em pedaços, para o porcupine processar
            frames_per_buffer=porcupine.frame_length
        )
        while True:
            #Lê um pedaço do audio
            pcm = audio_stream.read(porcupine.frame_length)
            #converte para int 16 bits
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            #processa com o porcupine
            keyword_index = porcupine.process(pcm)
            #se keyword_index for 0 ou maior, a palavra foi detectada.
            if keyword_index >= 0:
                print(f"Palavra de ativação '{palavra_chave}' detectada!")
                return
    finally:
        #garantir que tudo será fechado corretamente
        if audio_stream is not None:
            audio_stream.stop_stream()
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if porcupine is not None:
            porcupine.delete()
