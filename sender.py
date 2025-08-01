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
opts.add_argument(f"user-data‑dir={PROFILE}")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev‑shm‑usage")
opts.add_argument("--disable-gpu")
opts.add_argument("--remote-debugging-pipe")

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
time.sleep(15)
wait = WebDriverWait(driver, 30)
df = pd.read_excel(os.path.join(DATA_DIR, 'contatos.xlsx'), dtype=str)
df.columns = df.columns.str.strip().str.lower()

for _, row in df.iterrows():
    nome = row.get('nome') or row.get('name')
    numero = row.get('telefone') or row.get('phone') or row.get('numero')
    if not nome or not numero:
        print("Ignorando linha inválida:", row.to_dict())
        continue

    msg = template.format(nome=nome)
    if link:
        msg += f" Confira: {link}"

    url = f"https://web.whatsapp.com/send?phone={numero}&text={quote(msg)}"
    driver.get(url)

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='main']/footer")))
        time.sleep(2)
        campo = driver.find_element(By.XPATH, "//footer//div[@contenteditable='true']")
        campo.click()
        time.sleep(4)
        webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()

        print(f"✅ Mensagem enviada para: {nome}")
        with open(SENT_LOG, 'a+', encoding='utf-8') as f:
            f.write(f"{nome},{numero},{msg},{time.time()}\n")

    except Exception as ex:
        print(f"[sender] Erro ao enviar para {nome}:", ex)
    time.sleep(3)

driver.quit()
