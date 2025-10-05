#Esse script contém áudios pré-gravados para respostas comuns do assistente.
from gtts import gTTS # type: ignore
import os

print("Iniciando a geração de áudios...")

# Cria uma pasta chamada 'audios' para organizar os arquivos.
pasta_audios = "audios"
if not os.path.exists(pasta_audios):
    os.makedirs(pasta_audios)

# Dicionário com os nomes dos arquivos e as frases correspondentes.
frases_pregravadas = {
    "ouvindo": "Sim?",
    "verificando": "Só um momento, estou verificando.",
    "erro": "Desculpe, ocorreu um erro.",
    "processando": "Só um momento, estou processando...",
    "clima hoje": "Clima para hoje.",
}

# Loop para gerar e salvar cada arquivo de áudio.
for nome_arquivo, texto in frases_pregravadas.items():
    caminho_completo = os.path.join(pasta_audios, f"{nome_arquivo}.mp3")
    try:
        tts = gTTS(text=texto, lang='pt-br')
        tts.save(caminho_completo)
        print(f"Áudio '{caminho_completo}' gerado com sucesso.")
    except Exception as e:
        print(f"Falha ao gerar o áudio para '{texto}': {e}")

print("\nGeração de áudios concluída!")