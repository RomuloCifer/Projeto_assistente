#ferramentas para se comunicar com o sistema
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL # type: ignore
#classes para controlar o volume
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume # type: ignore


class ControladorVolume:
    def __init__(self):
        """Inicializa o controlador de volume."""
        #pegamos a interface de controle de volume
        self.interface = self._pegar_interface_volume()
        #pegamos o volume original
        self.volume_original = None
        ######################################
        if self.interface:
            print("[INFO] Controlador de volume inicializado com sucesso.")
        else:
            print("[ERRO] Falha ao inicializar o controlador de volume.")

    def _pegar_interface_volume(self):
        """Obtém a interface de controle de volume."""
        try:
            # Pegar o dispositivo de áudio padrão (alto-falantes)
            devices = AudioUtilities.GetSpeakers()
            # Ativar a interface de controle de volume
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            #o controle de volume é um ponteiro, então precisamos converter para o tipo correto
            return cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            print(f"Erro ao obter a interface de volume: {e}")
            return None
    def definir_volume(self,nivel):
        """Define o volume para um nível específico (0.0 a 1.0)."""
        if not self.interface:
            print("Interface de volume não disponível.")
            return
        try:
        #antes de mudar, salvamos o volume original
            self.volume_original = self.interface.GetMasterVolumeLevelScalar()
            print(f"[DIAG] Volume original salvo: {self.volume_original:.2f}. Abaixando para {nivel:.2f}.")
            #agora definimos o novo volume
            self.interface.SetMasterVolumeLevelScalar(nivel, None)
        except Exception as e:
            print(f"Erro ao definir o volume: {e}")
    def restaurar_volume(self):
        """Restaura o volume para o nível original."""
        if not self.interface:
            print("Interface de volume não disponível.")
            return
        if self.volume_original is not None:
            try:
                print(f"[DIAG] Restaurando volume para o nível original: {self.volume_original:.2f}.")
                self.interface.SetMasterVolumeLevelScalar(self.volume_original, None)
                self.volume_original = None #limpa o volume original depois de restaurar
            except Exception as e:
                print(f"Erro ao restaurar o volume: {e}")
        else:
            print("[AVISO] Volume original não foi salvo, nada para restaurar.")