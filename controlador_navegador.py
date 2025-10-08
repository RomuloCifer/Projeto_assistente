import os
from dotenv import load_dotenv # type: ignore
from selenium import webdriver # type: ignore
# #Importamos as opções para o navegador, para podermos iniciar em modo headless
from selenium.webdriver.chrome.options import Options as ChromeOptions # type: ignore
# Importamos a classe Service para configurar o driver
from selenium.webdriver.chrome.service import Service as ChromeService # type: ignore
# carrega as variaveis de ambiente.
load_dotenv()
chrome_caminho_executavel = os.getenv("CHROME_PROFILE_PATH")


class ControladorNavegador:
    def __init__(self):
        """Construtor, porém ainda não temos nenhum navegador ativo."""
        self.driver = None

    def iniciar_navegador(self, navegador='chrome', headless=True):
        """inicia o navegador, pode ser chrome. o headless que vai garantir que fique invisivel."""
        try:
            #Apesar de ser para o Opera, o webdriver do chrome funciona para ambos.
            options = ChromeOptions()
            if headless:
                options.add_argument('--headless')
                # Inicia o Chrome com as opções.
            #argumentos úteis para iniciar o navegador.
            options.add_argument('--start-maximized') #Inicia maximizado
            options.add_argument('--disable-infobars') #Desativa a barra de informações
            options.add_argument('--disable-extensions') #Desativa extensões
            servico = ChromeService(service_log_path=os.devnull)
            if navegador.lower() == 'opera':
                if not chrome_caminho_executavel:
                    raise ValueError("Caminho do Opera GX não encontrado.")
                #aponta para o executável do Opera GX
                options.binary_location = chrome_caminho_executavel
                self.driver = webdriver.Chrome(service=servico, options=options) # Usamos o driver do Chrome type: ignore
            elif navegador.lower() == 'chrome':
                self.driver = webdriver.Chrome(service=servico, options=options) # Usamos o driver do Chrome type: ignore
            else:
                raise ValueError("Navegador não suportado. Use 'chrome' ou 'opera'.")
            print(f"{navegador.capitalize()} Iniciado com sucesso.")
            return True
        except Exception as e:
            #Se algo der errado, printa o erro.
            print(f"Erro ao iniciar o navegador: {e}")
            return False
        

    def tocar_musica(self, video_url):
        """Função para tocar música pelo link recebido da API"""
        if not self.driver:
            print("Navegador não iniciado. Use iniciar_navegador primeiro.")
            return
        try:
            print(f"Tocando música pelo link: {video_url}")
            self.driver.get(video_url)
        except Exception as e:
            print(f"Erro ao tentar tocar música: {e}")


    def fechar_navegador(self):
        """Se o navegador estiver aberto, fecha ele."""
        if self.driver:
            self.driver.quit()
            self.driver = None
