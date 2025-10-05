from selenium import webdriver # type: ignore
#Importamos as opções para o navegador, para podermos iniciar em modo headless
from selenium.webdriver.chrome.options import Options as ChromeOptions # type: ignore


class ControladorNavegador:
    def __init__(self):
        """Construtor, porém ainda não temos nenhum navegador ativo."""
        self.driver = None

    def iniciar_navegador(self, navegador='chrome', headless=True):
        """inicia o navegador, pode ser chrome. o headless que vai garantir que fique invisivel."""
        try:
            #verifica o parâmetro, para rodar o navegador escolhido.
            if navegador.lower() == 'chrome':
                #criamos um objeto de opções para o Chrome.
                options = ChromeOptions()
                if headless:
                    options.add_argument('--headless')
                # Inicia o Chrome com as opções.
                self.driver = webdriver.Chrome(options=options)
            else:
                raise ValueError("Navegador não suportado. Use 'chrome' ou 'opera'.")
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
        print(f"Pesquisando por {nome_da_musica} no YouTube...")
        ...

    def fechar_navegador(self):
        """Se o navegador estiver aberto, fecha ele."""
        if self.driver:
            self.driver.quit()
            self.driver = None
