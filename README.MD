# 🤖 Bot WhatsApp - Sistema Automatizado

Sistema completo de automação do WhatsApp com envio em massa, transcrição de áudios e análise com IA.

## 📋 Funcionalidades

1. **Envio em Massa de Mensagens**
   - Personalização com templates (`{nome}`)
   - Suporte a links adicionais
   - Log de mensagens enviadas
   - Validação de números de telefone

2. **Escuta e Transcrição**
   - Monitor automático de chats
   - Transcrição de áudios com Google Speech Recognition
   - Log de mensagens recebidas
   - Suporte a múltiplos formatos de áudio

3. **Processamento com IA**
   - Análise de mensagens com GPT-3.5-turbo
   - Sugestões para melhorar comunicação
   - Foco em otimização de vendas

## 🚀 Instalação

### 1. Pré-requisitos
- Python 3.8+
- Google Chrome instalado
- ChromeDriver compatível

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto (use `config.env.example` como base):

```env
OPENAI_API_KEY=sua_chave_aqui
AI_ENDPOINT=https://api.openai.com/v1/chat/completions
```

### 4. Preparar arquivo de contatos
Crie ou edite o arquivo `data/contatos.xlsx` com as colunas:
- `nome` ou `name`: Nome do contato
- `telefone`, `phone` ou `numero`: Número do WhatsApp (com código do país)

Exemplo:
| nome  | telefone       |
|-------|----------------|
| João  | 5511999999999  |
| Maria | 5521888888888  |

## 💻 Como Usar

### Método 1: Interface Web (Recomendado)

```bash
python main.py
```

Acesse `http://localhost:8080` no navegador e use a interface gráfica.

### Método 2: Scripts Individuais

#### Enviar mensagens:
```bash
# Via variáveis de ambiente
MSG_TEMPLATE="Olá {nome}, como vai?" MSG_LINK="https://exemplo.com" python sender.py
```

#### Escutar e transcrever:
```bash
python listener_transcriber.py
```

#### Processar com IA:
```bash
python ai_process.py
```

## 📁 Estrutura de Arquivos

```
whatsapp_project/
├── main.py                    # Interface web (NiceGUI)
├── sender.py                  # Script de envio de mensagens
├── listener_transcriber.py    # Script de escuta e transcrição
├── ai_process.py              # Script de processamento com IA
├── requirements.txt           # Dependências Python
├── config.env.example         # Exemplo de configuração
├── data/
│   ├── contatos.xlsx          # Lista de contatos
│   ├── sent_log.csv           # Log de mensagens enviadas
│   ├── received_log.csv       # Log de mensagens recebidas
│   └── system.log             # Log do sistema
├── profile/                   # Perfil do Chrome (sessão do WhatsApp)
└── templates/                 # Templates HTML (legado)
```

## 🔧 Correções Implementadas

### ✅ Correções de Bugs
- ✅ Caracteres Unicode invisíveis em argumentos do Chrome corrigidos
- ✅ Encoding UTF-8 adicionado em todos os arquivos de log
- ✅ Configuração de download de áudios corrigida
- ✅ Validação de variáveis de ambiente adicionada

### ✅ Melhorias de Robustez
- ✅ Tratamento completo de exceções em todos os scripts
- ✅ Validação de dados de entrada (contatos, templates, arquivos)
- ✅ Limpeza automática de números de telefone
- ✅ Mensagens de erro descritivas
- ✅ Contadores de sucesso/erro

### ✅ Melhorias de Usabilidade
- ✅ Logs mais informativos com emojis e formatação
- ✅ Progresso de envio em tempo real
- ✅ Estatísticas ao final da execução
- ✅ Timeout de 30s para chamadas de API
- ✅ Retry automático para conexão com ChromeDriver

## ⚠️ Avisos Importantes

1. **Perfil do WhatsApp**: O primeiro uso requer login manual no WhatsApp Web. A sessão fica salva em `profile/`.

2. **Rate Limiting**: O WhatsApp pode bloquear contas que enviam muitas mensagens. Use com moderação.

3. **Estrutura HTML**: O WhatsApp atualiza frequentemente sua interface. Os XPaths podem precisar de ajuste.

4. **API da OpenAI**: Certifique-se de ter créditos na sua conta OpenAI.

## 🐛 Solução de Problemas

### ChromeDriver não encontrado
```bash
# Baixe o ChromeDriver compatível com sua versão do Chrome
# https://chromedriver.chromium.org/downloads
```

### Erro de transcrição de áudio
- Verifique sua conexão com a internet
- O Google Speech Recognition é gratuito mas tem limites

### Timeout no WhatsApp Web
- Aumente os valores de `time.sleep()` se sua conexão for lenta
- Verifique se o WhatsApp Web está carregando corretamente

### API da OpenAI retorna erro
- Verifique se a `OPENAI_API_KEY` está correta
- Confirme que há créditos na conta
- Verifique o status da API: https://status.openai.com/

## 📝 Logs

Todos os logs são salvos em:
- `data/system.log` - Log geral do sistema
- `data/sent_log.csv` - Histórico de mensagens enviadas
- `data/received_log.csv` - Histórico de mensagens recebidas

## 🔐 Segurança

- ⚠️ Nunca commite o arquivo `.env` com suas credenciais
- ⚠️ Mantenha a pasta `profile/` privada (contém sessão do WhatsApp)
- ⚠️ Use com responsabilidade e respeite a privacidade dos contatos

## 📜 Licença

Projeto para uso pessoal. Use com responsabilidade.

---

**Desenvolvido com ❤️ usando Python, Selenium e NiceGUI**

