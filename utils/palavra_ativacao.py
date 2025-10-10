#bibliotes para o detector de palavra.
import pyaudio # Para interagir com o mic. #type: ignore
import pvporcupine # O motor de detecção. #type: ignore
import struct # Para manipular os dados de áudio.
import os

class DetectorPalavraDeAtivacao:
    def __init__(self, access_key, palavra_chave: str = "pateta", sensitivity: float = 0.5, keyword_path: str = None, model_path: str = None):
        try:
            if keyword_path:
                # Verificar se o arquivo .ppn existe
                if not os.path.exists(keyword_path):
                    raise FileNotFoundError(f"Arquivo .ppn não encontrado: {keyword_path}")
                
                print(f"Usando arquivo .ppn: {keyword_path}")
                
                # Use custom .ppn file with optional custom model
                create_params = {
                    'access_key': access_key,
                    'keyword_paths': [keyword_path],
                    'sensitivities': [sensitivity]
                }
                
                # Add model path if provided
                if model_path:
                    if os.path.exists(model_path):
                        create_params['model_path'] = model_path
                        print(f"Usando modelo personalizado: {model_path}")
                    else:
                        print(f"Arquivo de modelo não encontrado: {model_path}")
                        print("Continuando sem modelo personalizado...")
                    
                self.porcupine = pvporcupine.create(**create_params)
                print("Porcupine inicializado com sucesso!")
            else:
                # Use built-in keywords
                self.porcupine = pvporcupine.create(
                    access_key=access_key,
                    keywords=[palavra_chave],
                    sensitivities=[sensitivity]
                )
            self.pa = pyaudio.PyAudio() #inicia o sistema que gerencia o áudio
            self.audio_stream = None
            self.palavra_chave = palavra_chave # salva a palavra chave
        except Exception as e: # se der algum erro, printa.
            print(f"Erro ao inicializar o detector de palavra de ativação: {e}")
            print(f"Dica: Certifique-se de que o arquivo .ppn e o modelo .pv sejam do mesmo idioma")
            if keyword_path:
                print(f"Arquivo .ppn: {keyword_path}")
            if model_path:
                print(f"Arquivo modelo: {model_path}")
            self.porcupine = None
    
    def iniciar_escuta(self):
        """Abre o fluxo de áudio e escuta ativamente pela palavra de ativação."""
        if not self.porcupine:
            print("Detector de palavra de ativação não inicializado corretamente.")
            return
        print(f"Esperando pela palavra de ativação '{self.palavra_chave}'...")
        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate, # taxa de amostragem que o porcupine espera
            channels=1, # mono
            format=pyaudio.paInt16, # formato de áudio (inteiro de 16 bits)
            input=True, # somente entrada
            frames_per_buffer=self.porcupine.frame_length # lê em pedaços do tamanho que o porcupine espera
        )
        #loop infinito, até a palavra aparecer.
        while True:
            try:
                pcm = self.audio_stream.read(self.porcupine.frame_length) # lê um pedaço do áudio
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm) # converte para int16

                #envia o áudio para o porcupine processar.
                keyword_index = self.porcupine.process(pcm)
                #se keyword_index for 0 ou maior, a palavra foi detectada.
                if keyword_index >= 0:
                    print(f"Palavra de ativação '{self.palavra_chave}' detectada!")
                    #fecha o microfone p/ liberar o recurso.
                    self._fechar_stream()
                    return
            except IOError as e:
                # Se ocorrer um erro de entrada/saída
                if e.errno == pyaudio.paInputOverflowed: # Se o buffer de entrada transbordar
                    pass  # Ignorar estouro de buffer
                else:
                    raise e # Re-raise outros erros
        
    def _fechar_stream(self):
        """Fecha o fluxo de áudio e libera o recurso."""
        if self.audio_stream is not None: # se o fluxo estiver aberto
            self.audio_stream.stop_stream() # para o fluxo
            self.audio_stream.close() # fecha o fluxo
            self.audio_stream = None # marca como fechado
    def fechar(self):
        """Libera todos os recursos."""
        self._fechar_stream() # fecha o fluxo se estiver aberto
        if self.pa is not None: # se o PyAudio estiver inicializado
            self.pa.terminate() # termina o PyAudio
            self.pa = None # marca como terminado
        if self.porcupine is not None: # se o Porcupine estiver inicializado
            self.porcupine.delete() # deleta o Porcupine
            self.porcupine = None # marca como deletado