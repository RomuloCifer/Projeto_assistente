# 🎙️ Assistente Virtual Inteligente

Um assistente virtual avançado em Python que combina reconhecimento de voz, processamento de linguagem natural com IA e múltiplas funcionalidades integradas.

## 📋 Índice

- [Características](#características)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração das APIs](#configuração-das-apis)
- [Uso](#uso)
- [Comandos Disponíveis](#comandos-disponíveis)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Contribuição](#contribuição)
- [Licença](#licença)

## ✨ Características

### 🔊 Reconhecimento de Voz
- Detecção de palavra de ativação personalizada ("Pateta")
- Reconhecimento de comandos em português brasileiro
- Feedback por voz com personalidade customizada

### 🧠 Inteligência Artificial
- Processamento de linguagem natural com Google Gemini
- Análise contextual de comandos
- Extração automática de entidades (datas, locais, etc.)

### 🌟 Funcionalidades Principais
- **Previsão do Tempo**: Consulta clima atual e futuro por cidade
- **Reprodução de Música**: Busca e reproduz músicas do YouTube
- **Gerenciamento de Agenda**: Criação de eventos no Google Calendar
- **Tradutor em Tempo Real**: Tradução automática do clipboard
- **Controle de Volume**: Gerenciamento inteligente de áudio por aplicativo
- **Data e Hora**: Informações temporais atualizadas

## 🔧 Pré-requisitos

### Sistema Operacional
- Windows 10/11 (testado)
- Python 3.8 ou superior

### Navegadores Suportados
- Google Chrome
- Opera GX

### Hardware
- Microfone funcional
- Alto-falantes ou fones de ouvido
- Conexão estável com a internet

## 📦 Instalação

### 1. Clone o Repositório
```bash
git clone <url-do-repositorio>
cd Projeto_assistente
```

### 2. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 3. Instale Dependências do Sistema

#### Chrome WebDriver
O ChromeDriver será instalado automaticamente pelo selenium-manager, mas certifique-se de ter o Chrome instalado.

#### PyAudio (Windows)
```bash
pip install pipwin
pipwin install pyaudio
```

## 🔑 Configuração das APIs

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Porcupine (Wake Word Detection) - https://console.picovoice.ai/
PORCUPINE_ACCESS_KEY="sua_chave_porcupine_aqui"

# OpenWeatherMap (Clima) - https://openweathermap.org/api
WEATHER_API_KEY="sua_chave_weather_aqui"

# Google Gemini (IA) - https://makersuite.google.com/app/apikey
GEMINI_API_KEY="sua_chave_gemini_aqui"

# YouTube Data API - https://console.cloud.google.com/
YOUTUBE_API_KEY="sua_chave_youtube_aqui"

# Configurações do Sistema
CHROME_PROFILE_PATH="caminho_para_seu_perfil_chrome"
ID_AGENDA="seu_email_google@gmail.com"

# Arquivos de Modelo (Português)
PATETA_PPN_PATH=c:\caminho\para\pateta.ppn
PORTUGUESE_MODEL_PATH=c:\caminho\para\porcupine_params_pt.pv
```

### 📝 Como Obter as Chaves de API

#### 1. Porcupine (Picovoice)
1. Acesse [Picovoice Console](https://console.picovoice.ai/)
2. Crie uma conta gratuita
3. Copie sua Access Key
4. Baixe os modelos em português se necessário

#### 2. OpenWeatherMap
1. Registre-se em [OpenWeatherMap](https://openweathermap.org/api)
2. Acesse "My API Keys"
3. Copie sua chave gratuita

#### 3. Google Gemini
1. Visite [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Faça login com sua conta Google
3. Crie uma nova API Key
4. Copie a chave gerada

#### 4. YouTube Data API
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a "YouTube Data API v3"
4. Crie credenciais (API Key)
5. Copie a chave gerada

#### 5. Google Calendar (Opcional)
Para usar o gerenciamento de agenda:
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Ative a "Google Calendar API"
3. Crie uma conta de serviço
4. Baixe o arquivo JSON das credenciais
5. Renomeie para `credentials_agenda.json`
6. Coloque na raiz do projeto

## 🚀 Uso

### Iniciar o Assistente
```bash
python assistente0.2.py
```

### Interação Básica
1. O assistente ficará em espera pela palavra de ativação
2. Diga **"Pateta"** para ativar
3. Aguarde o feedback sonoro
4. Fale seu comando claramente
5. O assistente processará e responderá

### Exemplo de Sessão
```
[Sistema] Esperando pela palavra de ativação 'pateta'...
[Usuário] "Pateta"
[Assistente] "Pois não?"
[Usuário] "Qual a previsão do tempo para São Paulo?"
[Assistente] "No momento, em São Paulo, está fazendo 22 graus Celsius e está parcialmente nublado."
```

## 🎯 Comandos Disponíveis

### 🌤️ Previsão do Tempo
- `"Qual o tempo em [cidade]?"`
- `"Como está o clima em [cidade]?"`
- `"Previsão para [cidade] amanhã"`

### 🎵 Reprodução de Música
- `"Tocar [nome da música]"`
- `"Reproduzir [artista - música]"`
- `"Colocar [música] para tocar"`

### 📅 Gerenciamento de Agenda
- `"Agendar [evento] para [data] às [hora]"`
- `"Marcar reunião amanhã às 15h"`
- `"Criar evento [nome] na [data]"`

### 🌐 Tradutor
- `"Iniciar tradutor"`
- `"Ativar modo tradução"`
- `"Parar tradutor"`

### ⏰ Data e Hora
- `"Que horas são?"`
- `"Qual a data de hoje?"`
- `"Me diga a hora atual"`

### 🚪 Encerramento
- `"Sair"`
- `"Desligar"`
- `"Tchau"`

## 📁 Estrutura do Projeto

```
Projeto_assistente/
│
├── assistente0.2.py              # Arquivo principal
├── requirements.txt              # Dependências
├── .env                          # Variáveis de ambiente (criar)
├── .gitignore                   # Arquivos ignorados pelo Git
├── README.md                    # Documentação
│
├── Habilidades/                 # Módulos de funcionalidades
│   ├── __init__.py
│   ├── analise.py              # Processamento com Gemini
│   ├── clima.py                # Previsão do tempo
│   ├── musica.py               # Integração YouTube
│   ├── gerenciar_agenda.py     # Google Calendar
│   ├── tradutor_clipboard.py   # Tradutor automático
│   ├── controlador_navegador.py # Controle web
│   └── controle_volume_updated.py # Gerenciamento áudio
│
└── utils/                       # Utilitários
    ├── __init__.py
    ├── funcoes_falar_ouvir.py   # TTS e STT
    ├── palavra_ativacao.py      # Detecção wake word
    └── personalidade.py         # Respostas personalizadas
```

## 🔧 Solução de Problemas

### Erro: "Arquivo .ppn não encontrado"
- Verifique se os caminhos no `.env` estão corretos
- Baixe os modelos em português do Porcupine se necessário

### Erro: "Chave de API não encontrada"
- Confirme se todas as chaves estão no arquivo `.env`
- Verifique se não há espaços extras nas chaves

### Erro de PyAudio no Windows
```bash
pip uninstall pyaudio
pip install pipwin
pipwin install pyaudio
```

### Erro de Microfone
- Verifique se o microfone está conectado e funcionando
- Teste com outros aplicativos de gravação
- Ajuste as permissões do microfone no Windows

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 Agradecimentos

- [Google](https://developers.google.com/) - APIs Gemini, YouTube, Calendar
- [OpenWeatherMap](https://openweathermap.org/) - Dados meteorológicos
- [Picovoice](https://picovoice.ai/) - Tecnologia de wake word
- [Python Speech Recognition](https://github.com/Uberi/speech_recognition) - Reconhecimento de voz

---

**Desenvolvido com ❤️ em Python**

Para suporte ou dúvidas, abra uma issue no repositório.
