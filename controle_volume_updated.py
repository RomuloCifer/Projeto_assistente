from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from comtypes import IUnknown, GUID
import psutil # Precisaremos desta nova biblioteca para pegar o nome do processo

class ControladorVolume:
    def __init__(self):
        """Inicializa o controlador. Agora, ele guarda os volumes de múltiplos aplicativos."""
        self.volumes_originais = {}
        print("[INFO] Controlador de volume por aplicativo inicializado.")

    def _pegar_nome_processo(self, pid):
        """Função auxiliar para obter o nome de um processo a partir do seu ID."""
        try:
            return psutil.Process(pid).name()
        except psutil.NoSuchProcess:
            return None

    def definir_volume_aplicativos(self, nivel_reducao, processos_ignorar=None):
        """
        Reduz o volume de todos os aplicativos com som, exceto os da lista para ignorar.
        
        Args:
            nivel_reducao (float): Fator de redução (ex: 0.2 para 20% do volume original).
            processos_ignorar (list): Lista de nomes de processos a não serem alterados (ex: ['python.exe']).
        """
        if processos_ignorar is None:
            processos_ignorar = []
            
        self.volumes_originais = {} # Limpa a lista de volumes salvos
        sessoes = AudioUtilities.GetAllSessions()
        
        print(f"[DIAG] Reduzindo volume para {nivel_reducao*100}%. Ignorando {processos_ignorar}...")
        for sessao in sessoes:
            if sessao.ProcessId: # Garante que a sessão pertence a um processo
                nome_processo = self._pegar_nome_processo(sessao.ProcessId)
                if nome_processo and nome_processo not in processos_ignorar:
                    try:
                        volume = sessao._ctl.QueryInterface(ISimpleAudioVolume)
                        volume_atual = volume.GetMasterVolume()
                        # Salva o ID do processo e seu volume original
                        self.volumes_originais[sessao.ProcessId] = volume_atual
                        # Define o novo volume (volume atual * fator de redução)
                        volume.SetMasterVolume(volume_atual * nivel_reducao, None)
                    except Exception:
                        # Algumas sessões (como sons do sistema) podem dar erro, então ignoramos
                        continue

    def restaurar_volume_aplicativos(self):
        """Restaura o volume de todos os aplicativos que foram alterados."""
        if not self.volumes_originais:
            # print("[DIAG] Nenhum volume de aplicativo para restaurar.")
            return

        print("[DIAG] Restaurando volume dos aplicativos...")
        sessoes = AudioUtilities.GetAllSessions()
        for sessao in sessoes:
            if sessao.ProcessId in self.volumes_originais:
                try:
                    volume = sessao._ctl.QueryInterface(ISimpleAudioVolume)
                    # Restaura o volume salvo usando o ID do processo
                    volume_original = self.volumes_originais[sessao.ProcessId]
                    volume.SetMasterVolume(volume_original, None)
                except Exception:
                    continue
        
        self.volumes_originais = {} # Limpa o dicionário após restaurar