import pyperclip
import time


def mostrar_popup(texto_traduzido):
    """Cria e exibe uma janela pop-up sem bordas na posição do mouse."""
    import tkinter as tk
    import pyautogui
    x, y = pyautogui.position() # Pega a posição atual do mouse
    popup = tk.Tk() # Cria a janela principal
    popup.overrideredirect(True) # Remove bordas e barra de título
    popup.wm_attributes("-topmost", True) # Mantém a janela no topo
    popup.wm_attributes("-alpha", 0.7) # Define a transparência da janela (0.0 a 1.0)
    popup.geometry(f"+{x + 15}+{y + 10}") # Posiciona a janela próxima ao mouse

    label = tk.Label(
        popup,
        text=texto_traduzido,
        font=("Arial", 10, "bold"), # negrito
        bg="#FFFFE0", # cor de fundo amarelo claro
        padx=10, pady=10, # padding interno
        justify=tk.LEFT, # alinha o texto à esquerda
        wraplength=300 # quebra de linha após 300 pixels
    )
    label.pack() 
    popup.after(3000, popup.destroy) # Fecha o pop-up após 3 segundos
    popup.mainloop() # Inicia o loop principal do Tkinter, que desenha a janela.

def traduzir_texto(texto, dest='pt', src='auto'):
    from deep_translator import GoogleTranslator
    """
    Função que recebe um texto e retorna a tradução usando a deep_translator.
    """
    try:
        # A forma de chamar o tradutor mudou um pouco
        resultado = GoogleTranslator(source=src, target=dest).translate(texto)
        return resultado
    
    except Exception as e:
        print(f"Ocorreu um erro na tradução: {e}")
        return None

def monitorar_clipboard():
    """
    Função principal que monitora a área de transferência.
    (Esta função não precisou de grandes mudanças)
    """
    print("Tradutor de clipboard iniciado. Copie um texto para traduzir (Ctrl+C).")
    print("Pressione Ctrl+C no terminal para encerrar.")
    
    texto_recente = ""

    while True:
        try:
            texto_copiado = pyperclip.paste()

            if texto_copiado and texto_copiado != texto_recente:
                texto_recente = texto_copiado
                
                print("-" * 30)
                print(f"Texto copiado: {texto_copiado}")
                
                resultado_traducao = traduzir_texto(texto_copiado)
                
                if resultado_traducao:
                    mostrar_popup(resultado_traducao) # Mostra o pop-up com a tradução
                
            time.sleep(1)

        except KeyboardInterrupt:
            print("\nTradutor encerrado.")
            break
        except Exception as e:
            print(f"Ocorreu um erro no loop principal: {e}")
            time.sleep(2)


if __name__ == "__main__":
    monitorar_clipboard()