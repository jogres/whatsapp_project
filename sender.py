import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from urllib.parse import quote

PROFILE = os.path.abspath('profile')
DATA_DIR = os.path.abspath('data')
SENT_LOG = os.path.join(DATA_DIR, 'sent_log.csv')
os.makedirs(DATA_DIR, exist_ok=True)
open(SENT_LOG, 'a+', encoding='utf-8').close()

# Template e link vêm do frontend via env
template = os.getenv('MSG_TEMPLATE', 'Olá {nome}, tudo bem?')
link = os.getenv('MSG_LINK', '').strip()

opts = Options()
opts.add_argument(f"user-data-dir={PROFILE}")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--disable-gpu")
opts.add_argument("--remote-debugging-pipe")
opts.add_experimental_option("prefs", {
    "download.default_directory": DATA_DIR,
    "download.prompt_for_download": False,
})

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
print("Aguardando 15 segundos para login no WhatsApp Web...")
time.sleep(15)

wait = WebDriverWait(driver, 30)

# Ler arquivo de contatos
contatos_file = os.path.join(DATA_DIR, 'contatos.xlsx')
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
        print(f"❌ Linha {idx+1}: Dados inválidos (nome ou número faltando)")
        erros += 1
        continue
    
    # Limpar número (remover espaços, hífens, parênteses)
    numero = str(numero).strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    if not numero.isdigit():
        print(f"❌ Linha {idx+1}: Número inválido para {nome}: {numero}")
        erros += 1
        continue

    try:
        msg = template.format(nome=nome)
    except KeyError as e:
        print(f"❌ Erro no template: variável {e} não encontrada. Use {{nome}} no template.")
        erros += 1
        continue
    
    if link:
        msg += f" Confira: {link}"

    url = f"https://web.whatsapp.com/send?phone={numero}&text={quote(msg)}"
    
    print(f"\n[{idx+1}/{len(df)}] Enviando para: {nome} ({numero})")
    
    try:
        driver.get(url)
        
        # Esperar footer carregar (indica que o chat abriu)
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='main']/footer")))
        time.sleep(2)
        
        # Localizar campo de mensagem
        campo = driver.find_element(By.XPATH, "//footer//div[@contenteditable='true']")
        campo.click()
        time.sleep(2)
        
        # Enviar mensagem
        webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
        time.sleep(2)

        print(f"✅ Mensagem enviada para: {nome}")
        
        # Registrar envio
        with open(SENT_LOG, 'a+', encoding='utf-8') as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp},{nome},{numero},{msg}\n")
        
        enviados += 1

    except Exception as ex:
        print(f"❌ Erro ao enviar para {nome}: {ex}")
        erros += 1
    
    # Delay entre envios
    time.sleep(3)

print(f"\n{'='*60}")
print(f"✅ Concluído!")
print(f"   Enviados: {enviados}")
print(f"   Erros: {erros}")
print(f"   Total: {len(df)}")
print(f"{'='*60}")

driver.quit()
