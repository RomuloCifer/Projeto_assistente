import os
from dotenv import load_dotenv # type: ignore

def pesquisar_musica_youtube(nome_musica):
    from googleapiclient.discovery import build # type: ignore
    load_dotenv()
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    if not YOUTUBE_API_KEY:
        raise ValueError("Chave de API do YouTube não encontrada.")
    """Busca uma música no Youtube usando a API do Youtube e retorna o link do primeiro resultado"""
    try:
        #Inicia o serviço da API do youtube
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        #faz a chamada para a API
        request = youtube.search().list(
            q=nome_musica,
            part='snippet', # informações básicas como título, descrição, nome do canal, etc.
            maxResults=5, # 5 primeiros resultados
            type='video',
            topicId='/m/04rlf'  # ID do google para Música. (melhora a relevância dos resultados)
        )
        #Agora enviamos a requisição
        response = request.execute()
        #A resposta vem com vários dados, o 'items' é a lista de vídeos encontrados
        videos = response.get('items', [])
        #se a lista vier vazia.
        if not videos:
            return None
        prioridades = ['Official Music Video', 'Official Video', 'Music Video', 'Audio', 'Lyric Video']
        # Criamos uma lista para armazenar os resultados válidos
        resultados_validos = []
        
        #Uma filtragem iniciar para garantir somente vídeos válidos, ignorando canais ou playlists
        for item in videos:
            if 'videoId' in item['id']:
                resultados_validos.append(item)
        if not resultados_validos:
            return None
        #passamos pelos resultados válidos procurando por títulos prioritários
        for video in resultados_validos:
            titulo_video = video['snippet']['title'].lower()
            for p in prioridades:
                if p.lower() in titulo_video:
                    video_id = video['id']['videoId']
                    # Se encontrarmos um vídeo prioritário, informamos no console e o retornamos imediatamente.
                    print(f"Resultado priorizado encontrado: {video['snippet']['title']}")
                    return video['id']['videoId'] # O ID do vídeo é o que precisamos para a URL.
                #Se não encontrar nada prioritário, retorna o primeiro resultado.
                return resultados_validos[0]['id']['videoId']
    except Exception as e:
        print(f"Erro ao buscar música no YouTube: {e}")
        return None
