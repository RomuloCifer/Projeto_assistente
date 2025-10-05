import os
from dotenv import load_dotenv
from selenium import webdriver # type: ignore
# #Importamos as opções para o navegador, para podermos iniciar em modo headless
from selenium.webdriver.chrome.options import Options as ChromeOptions # type: ignore
# Importamos a classe Service para configurar o driver
from selenium.webdriver.chrome.service import Service as ChromeService # type: ignore
# Como vamos encontrar elementos na página pelo ID, nome, classe, etc.
from selenium.webdriver.common.by import By
#Para esperar os elementos carregarem, sem precisar usar time.sleep
from selenium.webdriver.support.ui import WebDriverWait
# para definir condições de espera. Ex: esperar até que um elemento seja clicável, ou até que ele esteja visível.
from selenium.webdriver.support import expected_conditions as EC
# Para simular teclas do teclado, como ENTER, ESC, etc...
from selenium.webdriver.common.keys import Keys
# carrega as variaveis de ambiente.
load_dotenv()
opera_caminho_executavel = os.getenv("OPERA_GX_PATH")


class ControladorNavegador:
    def __init__(self):
        """Construtor, porém ainda não temos nenhum navegador ativo."""
        self.driver = None

    def iniciar_navegador(self, navegador='chrome', headless=False):
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
                if not opera_caminho_executavel:
                    raise ValueError("Caminho do Opera GX não encontrado.")
                #aponta para o executável do Opera GX
                options.binary_location = opera_caminho_executavel
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
        

    def tocar_musica(self,nome_da_musica):
        """Função para tocar uma música no Youtube."""
        if not self.driver:
            print("Navegador não iniciado. Use iniciar_navegador primeiro.")
            return
        try:
            print(f"Pesquisando por {nome_da_musica} no YouTube...")
            self.driver.get("https://www.youtube.com")
            #criamos um objeto que espera os elementos carregarem. 10 segundos é o tempo máx.
            wait = WebDriverWait(self.driver, 10)

            # Usamos o 'wait' para esperar até que o elemento com o atributo name="search_query" (a barra de pesquisa) esteja visível
            search_box = wait.until(EC.visibility_of_element_located((By.NAME, "search_query")))
            search_box.clear()  # Limpa a barra de pesquisa
            search_box.send_keys(nome_da_musica)  # Digita o nome da música 
            search_box.send_keys(Keys.RETURN)  # Pressiona Enter para pesquisar

            # Espera até que os resultados da pesquisa estejam visíveis.
            primeiro_video = wait.until(EC.visibility_of_element_located((By.ID, "video-title")))
            primeiro_video.click()  # Clica no primeiro vídeo da lista
            print(f"Tocando {nome_da_musica} no YouTube.")
        except Exception as e:
            print(f"Erro ao tentar tocar música: {e}")
        

    def fechar_navegador(self):
        """Se o navegador estiver aberto, fecha ele."""
        if self.driver:
            self.driver.quit()
            self.driver = None
