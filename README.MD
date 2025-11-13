# 🤖 Bot WhatsApp - Envio de Mensagens em Massa

Sistema simples, eficiente e **portável** para envio de mensagens em massa via WhatsApp Web.

## 📋 Funcionalidades

- ✅ Envio em massa de mensagens personalizadas
- ✅ Templates com variáveis (`{nome}`)
- ✅ Suporte a links adicionais
- ✅ Interface web amigável
- ✅ Log de mensagens enviadas
- ✅ Validação de números de telefone
- ✅ **Sistema portável** - pode ser transportado para outros dispositivos
- ✅ **Modo portável** - não salva login do WhatsApp (login a cada uso)

## 🚀 Instalação

### 1. Pré-requisitos
- Python 3.8+
- Google Chrome instalado
- ChromeDriver compatível

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Preparar arquivo de contatos
Crie ou edite o arquivo `data/contatos.xlsx` com as colunas:
- `nome` ou `name`: Nome do contato
- `telefone`, `phone` ou `numero`: Número do WhatsApp (com código do país)

Exemplo:
| nome  | telefone       |
|-------|----------------|
| João  | 5511999999999  |
| Maria | 5521888888888  |

## 💻 Como Usar

### Interface Web (Recomendado)

```bash
python main.py
```

Acesse `http://localhost:8080` no navegador e use a interface gráfica.

**Recursos da Interface:**
- Campo de mensagem com template personalizado
- Campo para link adicional
- **Switch para modo portável** (desligado = login toda vez, ligado = salva login)
- Botões para iniciar/parar envio
- Log em tempo real

### 🔄 Modo Portável (Padrão)

Por padrão, o sistema está configurado em **modo portável**:
- ✅ **Não salva o login do WhatsApp** - você precisa fazer login a cada execução
- ✅ **Perfil temporário** - criado e removido automaticamente
- ✅ **Totalmente portável** - pode copiar a pasta para outro dispositivo
- ✅ **Mais seguro** - não deixa rastros de sessão

**Como funciona:**
1. Ao iniciar o envio, o Chrome abrirá com WhatsApp Web
2. Escaneie o QR Code com seu celular
3. O sistema aguardará até 2 minutos para você fazer login
4. Após o login, o envio começará automaticamente
5. Ao finalizar, o perfil temporário é removido

### 💾 Modo com Perfil Persistente (Opcional)

Se preferir salvar o login:
1. Na interface, ative o switch "💾 Usar perfil persistente"
2. Na primeira execução, faça login normalmente
3. Nas próximas execuções, o login será mantido
4. O perfil será salvo em `profile/` (não portável)

### Linha de Comando

```bash
# Via variáveis de ambiente
MSG_TEMPLATE="Olá {nome}, como vai?" MSG_LINK="https://exemplo.com" python sender.py
```

## 📁 Estrutura de Arquivos

```
whatsapp_project/
├── main.py                    # Interface web (NiceGUI)
├── sender.py                  # Script de envio de mensagens
├── requirements.txt           # Dependências Python
├── README.MD                  # Este arquivo
├── data/
│   ├── contatos.xlsx          # Lista de contatos
│   ├── sent_log.csv           # Log de mensagens enviadas
│   └── system.log             # Log do sistema
└── profile/                   # Perfil do Chrome (apenas se usar modo persistente)
```

**Nota:** A pasta `profile/` só é criada se você usar o modo com perfil persistente. No modo portável (padrão), um perfil temporário é criado e removido automaticamente.

## ⚠️ Avisos Importantes

1. **Login no WhatsApp**: 
   - **Modo portável (padrão)**: Você precisa fazer login a cada execução escaneando o QR Code. A sessão **não é salva**.
   - **Modo persistente (opcional)**: O primeiro uso requer login manual, depois a sessão fica salva em `profile/`

2. **Portabilidade**: O sistema usa caminhos relativos, então você pode copiar toda a pasta para outro dispositivo e usar normalmente (no modo portável).

3. **Rate Limiting**: O WhatsApp pode bloquear contas que enviam muitas mensagens. Use com moderação e respeite os limites.

4. **Estrutura HTML**: O WhatsApp atualiza frequentemente sua interface. Os seletores podem precisar de ajuste.

## 🐛 Solução de Problemas

### ChromeDriver não encontrado
```bash
# Baixe o ChromeDriver compatível com sua versão do Chrome
# https://chromedriver.chromium.org/downloads
```

### Timeout no WhatsApp Web
- Aumente os valores de `time.sleep()` se sua conexão for lenta
- Verifique se o WhatsApp Web está carregando corretamente

### Mensagens duplicadas
- O sistema foi configurado para evitar duplicação
- Se ocorrer, verifique se não há múltiplas instâncias rodando

## 📝 Logs

Todos os logs são salvos em:
- `data/system.log` - Log geral do sistema
- `data/sent_log.csv` - Histórico de mensagens enviadas

## 🔐 Segurança

- ⚠️ **Modo portável é mais seguro** - não deixa rastros de sessão do WhatsApp
- ⚠️ Se usar modo persistente, mantenha a pasta `profile/` privada (contém sessão do WhatsApp)
- ⚠️ Use com responsabilidade e respeite a privacidade dos contatos
- ⚠️ Não compartilhe a pasta `profile/` com outras pessoas

## 📜 Licença

Projeto para uso pessoal. Use com responsabilidade.

---

**Desenvolvido com ❤️ usando Python, Selenium e NiceGUI**
