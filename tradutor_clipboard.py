import pyperclip
import time


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
                    # A resposta da nova biblioteca é mais direta
                    print(f"Tradução: {resultado_traducao}")
                
            time.sleep(1)

        except KeyboardInterrupt:
            print("\nTradutor encerrado.")
            break
        except Exception as e:
            print(f"Ocorreu um erro no loop principal: {e}")
            time.sleep(2)


if __name__ == "__main__":
    monitorar_clipboard()