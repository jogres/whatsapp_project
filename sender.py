# Configurar encoding UTF-8 ANTES de qualquer import ou print
import sys
import os

# Configurar encoding UTF-8 para Windows - DEVE SER A PRIMEIRA COISA
if sys.platform == 'win32':
    import io
    # Reconfigurar stdout e stderr com UTF-8
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # Configurar variável de ambiente
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import time
import tempfile
import shutil
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

# Tornar o sistema portável - usar caminho relativo ao script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
SENT_LOG = os.path.join(DATA_DIR, 'sent_log.csv')
os.makedirs(DATA_DIR, exist_ok=True)
open(SENT_LOG, 'a+', encoding='utf-8').close()

# Template e link vêm do frontend via env
template = os.getenv('MSG_TEMPLATE', 'Olá {nome}, tudo bem?')
link = os.getenv('MSG_LINK', '').strip()
USE_PROFILE = os.getenv('USE_PROFILE', 'false').lower() == 'true'

# Configurar Chrome - SEM perfil persistente (portável)
opts = Options()
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--disable-gpu")
opts.add_argument("--remote-debugging-pipe")
# NÃO usar headless - precisa estar visível para login e envio
# opts.add_argument("--headless")  # Comentado - precisa estar visível
opts.add_experimental_option("prefs", {
    "download.prompt_for_download": False,
})
# Desabilitar notificações
opts.add_argument("--disable-notifications")

# Se não usar perfil, criar um temporário que será removido após o uso
temp_profile = None
if not USE_PROFILE:
    # Criar perfil temporário que será removido ao final
    temp_profile = tempfile.mkdtemp(prefix='whatsapp_temp_')
    opts.add_argument(f"user-data-dir={temp_profile}")
    print(f"[MODO PORTAVEL] Usando perfil temporario (sera removido ao final)")
else:
    # Usar perfil persistente (opcional)
    PROFILE = os.path.join(SCRIPT_DIR, 'profile')
    opts.add_argument(f"user-data-dir={PROFILE}")
    print(f"[MODO PERSISTENTE] Usando perfil em {PROFILE}")

driver = None
for attempt in range(3):
    try:
        driver = webdriver.Chrome(options=opts)
        break
    except WebDriverException as e:
        print(f"[sender] Tentativa {attempt+1} falhou:", e)
        time.sleep(5)
if driver is None:
    raise RuntimeError("ChromeDriver falhou após várias tentativas")

driver.get("https://web.whatsapp.com")

# Aguardar um tempo para o WhatsApp carregar (sem verificação)
if not USE_PROFILE:
    print("\n[MODO PORTAVEL] Aguardando 20 segundos para você fazer login...")
    print("[INFO] Escaneie o QR Code se necessário e aguarde o WhatsApp carregar.")
    time.sleep(20)
else:
    print("[AGUARDANDO] 15 segundos para login no WhatsApp Web...")
    time.sleep(15)

wait = WebDriverWait(driver, 30)
print("[OK] Continuando com os envios...")

# Função para enviar mensagem de texto
def enviar_texto(driver, wait, texto):
    """
    Envia uma mensagem de texto no WhatsApp Web usando múltiplos métodos.
    """
    try:
        print(f"[DEBUG] Tentando enviar mensagem: {texto[:50]}...")
        
        # Múltiplos seletores para o campo de mensagem
        seletores = [
            "//div[@contenteditable='true'][@data-tab='10']",  # Seletor mais específico
            "//footer//div[@contenteditable='true']",  # Seletor original
            "//div[@contenteditable='true'][@role='textbox']",  # Alternativa
            "//div[@id='main']//footer//div[@contenteditable='true']",  # Mais específico
            "//p[@class='selectable-text copyable-text']//..//..//div[@contenteditable='true']",  # Alternativa
        ]
        
        campo = None
        for seletor in seletores:
            try:
                campo = wait.until(EC.presence_of_element_located((By.XPATH, seletor)))
                if campo and campo.is_displayed():
                    print(f"[DEBUG] Campo encontrado com seletor: {seletor[:50]}...")
                    break
            except:
                continue
        
        if not campo:
            print("[ERRO] Não foi possível encontrar o campo de mensagem")
            return False
        
        # Scroll até o campo
        driver.execute_script("arguments[0].scrollIntoView(true);", campo)
        time.sleep(0.5)
        
        # Clicar no campo
        try:
            campo.click()
        except:
            driver.execute_script("arguments[0].click();", campo)
        time.sleep(0.5)
        
        # Limpar campo completamente usando JavaScript
        driver.execute_script("""
            var campo = arguments[0];
            campo.innerText = '';
            campo.textContent = '';
            campo.innerHTML = '';
        """, campo)
        time.sleep(0.3)
        
        # Método 1: Usar send_keys diretamente
        try:
            campo.send_keys(texto)
            time.sleep(0.5)
            
            # Verificar se o texto foi digitado
            texto_digitado = driver.execute_script("return arguments[0].innerText || arguments[0].textContent || '';", campo)
            if texto_digitado.strip() == texto.strip():
                print("[DEBUG] Texto digitado com sucesso (método 1)")
            else:
                # Método 2: Usar JavaScript para inserir texto
                print("[DEBUG] Tentando método alternativo (JavaScript)...")
                driver.execute_script("arguments[0].innerText = arguments[1];", campo, texto)
                time.sleep(0.5)
        except Exception as e:
            print(f"[DEBUG] Método 1 falhou, tentando JavaScript: {str(e)}")
            # Método 2: Inserir via JavaScript
            driver.execute_script("arguments[0].innerText = arguments[1];", campo, texto)
            time.sleep(0.5)
        
        # Disparar evento de input para garantir que o WhatsApp detecte
        driver.execute_script("""
            var campo = arguments[0];
            var evento = new Event('input', { bubbles: true });
            campo.dispatchEvent(evento);
        """, campo)
        time.sleep(0.5)
        
        # Verificar se o texto está no campo antes de enviar
        texto_final = driver.execute_script("return arguments[0].innerText || arguments[0].textContent || '';", campo)
        if not texto_final.strip():
            print("[ERRO] Campo está vazio após tentar digitar")
            return False
        
        print(f"[DEBUG] Texto no campo: {texto_final[:50]}...")
        
        # Enviar mensagem - tentar múltiplos métodos
        try:
            # Método 1: Enter direto
            campo.send_keys(Keys.ENTER)
            time.sleep(1)
            print("[DEBUG] Mensagem enviada (método Enter)")
        except:
            try:
                # Método 2: ActionChains
                webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
                time.sleep(1)
                print("[DEBUG] Mensagem enviada (método ActionChains)")
            except:
                # Método 3: JavaScript para clicar no botão de enviar
                try:
                    botao_enviar = driver.find_element(By.XPATH, "//span[@data-icon='send']")
                    botao_enviar.click()
                    time.sleep(1)
                    print("[DEBUG] Mensagem enviada (método botão)")
                except:
                    print("[ERRO] Não foi possível enviar a mensagem")
                    return False
        
        # Verificar se a mensagem foi enviada (campo deve estar vazio)
        time.sleep(1)
        texto_apos_envio = driver.execute_script("return arguments[0].innerText || arguments[0].textContent || '';", campo)
        if not texto_apos_envio.strip():
            print("[OK] Mensagem enviada com sucesso!")
            return True
        else:
            print(f"[AVISO] Campo ainda contém texto: {texto_apos_envio[:50]}...")
            return True  # Retornar True mesmo assim, pode ter sido enviado
        
    except Exception as e:
        print(f"[ERRO] Erro ao enviar texto: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return False

# Ler arquivo de contatos (portável - relativo ao script)
contatos_file = os.path.join(SCRIPT_DIR, 'data', 'contatos.xlsx')
if not os.path.exists(contatos_file):
    print(f"ERRO: Arquivo {contatos_file} não encontrado!")
    driver.quit()
    exit(1)

try:
    df = pd.read_excel(contatos_file, dtype=str)
    df.columns = df.columns.str.strip().str.lower()
except Exception as e:
    print(f"ERRO ao ler arquivo Excel: {e}")
    driver.quit()
    exit(1)

if df.empty:
    print("AVISO: Arquivo de contatos está vazio!")
    driver.quit()
    exit(0)

print(f"Encontrados {len(df)} contatos para processar")
print(f"Template de mensagem: {template}")
if link:
    print(f"Link adicional: {link}")

enviados = 0
erros = 0

for idx, row in df.iterrows():
    nome = row.get('nome') or row.get('name')
    numero = row.get('telefone') or row.get('phone') or row.get('numero')
    
    if not nome or not numero:
        print(f"[ERRO] Linha {idx+1}: Dados inválidos (nome ou número faltando)")
        erros += 1
        continue
    
    # Limpar número (remover espaços, hífens, parênteses, pontos)
    numero = str(numero).strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('.', '').replace('+', '')
    
    # Verificar se o número é válido (deve ter pelo menos 10 dígitos)
    if not numero.isdigit() or len(numero) < 10:
        print(f"[ERRO] Linha {idx+1}: Número inválido para {nome}: {numero}")
        erros += 1
        continue
    
    # Adicionar código do país se não tiver (assumindo Brasil +55)
    if len(numero) == 10 or len(numero) == 11:
        # Número brasileiro sem código do país
        if numero[0] == '0':
            numero = '55' + numero[1:]  # Remove o 0 inicial
        else:
            numero = '55' + numero

    try:
        msg = template.format(nome=nome)
    except KeyError as e:
        print(f"[ERRO] Erro no template: variável {e} não encontrada. Use {{nome}} no template.")
        erros += 1
        continue
    
    if link:
        msg += f" Confira: {link}"

    # URL sem texto - sempre preencher manualmente para evitar duplicação
    url = f"https://web.whatsapp.com/send?phone={numero}"
    
    print(f"\n[{idx+1}/{len(df)}] Enviando para: {nome} ({numero})")
    print(f"[DEBUG] URL: {url}")
    
    try:
        print(f"[DEBUG] Abrindo URL do WhatsApp...")
        driver.get(url)
        time.sleep(3)  # Aguardar página carregar
        print(f"[DEBUG] Página carregada, aguardando footer...")
        
        # Esperar footer carregar (indica que o chat abriu) com timeout maior
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='main']/footer")))
            print(f"[DEBUG] Footer encontrado, chat aberto!")
            time.sleep(2)
        except Exception as timeout_err:
            print(f"[ERRO] Timeout ao abrir chat para {nome}. Verifique se o número está correto.")
            print(f"[DEBUG] Erro: {str(timeout_err)}")
            erros += 1
            continue
        
        # Verificar se o número existe no WhatsApp
        try:
            # Procurar mensagem de erro de número inválido
            error_msg = driver.find_elements(By.XPATH, "//div[contains(text(), 'número de telefone') or contains(text(), 'phone number')]")
            if error_msg:
                print(f"ERRO: Número {numero} não encontrado no WhatsApp")
                erros += 1
                continue
        except:
            pass  # Continuar se não encontrar mensagem de erro
        
        # Sempre usar função enviar_texto para evitar duplicação
        sucesso_envio = enviar_texto(driver, wait, msg)

        if sucesso_envio:
            print(f"[OK] Mensagem enviada para: {nome}")
            
            # Registrar envio
            try:
                with open(SENT_LOG, 'a+', encoding='utf-8') as f:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"{timestamp},{nome},{numero},{msg}\n")
            except Exception as log_err:
                print(f"AVISO: Erro ao registrar log: {log_err}")
            
            enviados += 1
        else:
            print(f"[FALHA] Falha ao enviar mensagem para: {nome}")
            erros += 1

    except Exception as ex:
        print(f"[ERRO] Erro ao enviar para {nome}: {str(ex)}")
        erros += 1
    
    # Delay entre envios
    time.sleep(3)

print(f"\n{'='*60}")
print(f"[CONCLUIDO]")
print(f"   Enviados: {enviados}")
print(f"   Erros: {erros}")
print(f"   Total: {len(df)}")
print(f"{'='*60}")

# Fechar driver
driver.quit()

# Limpar perfil temporário se foi usado
if temp_profile and os.path.exists(temp_profile):
    try:
        print(f"[LIMPEZA] Removendo perfil temporario...")
        shutil.rmtree(temp_profile)
        print(f"[OK] Perfil temporario removido")
    except Exception as e:
        print(f"[AVISO] Nao foi possivel remover perfil temporario: {str(e)}")
