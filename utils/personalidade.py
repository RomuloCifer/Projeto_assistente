import random

respostas = {
    # Resposta quando a palavra de ativação é detectada
    'saudacao_ativacao': [
        "Sim?",
        "Pois não?",
        "Estou aqui.",
        "O que precisa?",
        "Às ordens."
    ],
    # Frases para indicar que um processo demorado começou
    'processando': [
        "Só um momento, estou processando...",
        "Ok, um segundo.",
        "Aguarde um instante.",
        "Deixa comigo, estou verificando."
    ],
    # Respostas genéricas para quando algo dá errado
    'erro_generico': [
        "Desculpe, ocorreu um erro.",
        "Opa, algo deu errado aqui.",
        "Não consegui completar a ação.",
        "Encontrei um problema ao tentar fazer isso."
    ],
    # Confirmação genérica de execução
    'confirmacao_execucao': [
        "Ok, entendido.",
        "Anotado!",
        "Pode deixar.",
        "Pra já!"
    ],
    # Mensagens de despedida
    'despedida': [
        "Encerrando. Até mais!",
        "Desligando. A gente se fala depois.",
        "Até a próxima!"
    ],

    'musica_tocando': [
        "Claro, tocando {musica} agora mesmo.",
        "Boa escolha! Colocando {musica} pra tocar.",
        "Aumenta o som! Tocando {musica} no YouTube.",
        "Pra já! Iniciando {musica}."
]
}

def obter_resposta_personalidade(categoria):
    """resposta aleatória com base na categoria fornecida."""
    if categoria in respostas:
        return random.choice(respostas[categoria])
    #resposta padrão se a categoria não for encontrada
    return "Categoria de resposta não encontrada."