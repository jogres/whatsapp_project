import os, time, glob
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import WebDriverException
from speech_recognition import Recognizer, AudioFile

# diretórios importantes
PROFILE = os.path.abspath("profile")
DATA_DIR = os.path.abspath("data")
RECV_LOG = os.path.join(DATA_DIR, "received_log.csv")
os.makedirs(DATA_DIR, exist_ok=True)
open(RECV_LOG, "a").close()

# configurar ChromeOptions
opts = Options()
opts.add_argument(f"user-data-dir={PROFILE}")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--disable-gpu")
# opcional:
# opts.add_argument("--headless")
opts.add_argument("--remote-debugging-pipe")

# tentar criar driver com retry
driver = None
for attempt in range(3):
    try:
        driver = webdriver.Chrome(options=opts)
        break
    except WebDriverException as e:
        print(f"[listener] Tentativa {attempt+1} falhou:", e)
        time.sleep(5)
if driver is None:
    raise RuntimeError("ChromeDriver falhou após 3 tentativas")

driver.get("https://web.whatsapp.com")
time.sleep(15)
recognizer = Recognizer()

def process_message(msg, ts):
    if not driver.session_id:
        raise RuntimeError("Sessão inválida — reinicie o browser")
    if msg.find_elements(By.TAG_NAME, "audio"):
        ActionChains(driver).move_to_element(
            msg.find_element(By.XPATH, ".//span[@data-icon='menu']")
        ).click()
        time.sleep(1)
        driver.find_element(By.XPATH, "//li[@data-testid='download']").click()
        time.sleep(5)
        transcript = ""
        files = sorted(glob.glob(os.path.join(DATA_DIR, "*.ogg")) +
                       glob.glob(os.path.join(DATA_DIR, "*.mp3")),
                       key=os.path.getmtime)
        if files:
            path = files[-1]
            with AudioFile(path) as src:
                audio = recognizer.record(src)
                try:
                    transcript = recognizer.recognize_google(audio, language="pt-BR")
                except Exception as e:
                    transcript = f"<error:{e}>"
            os.remove(path)
        content = f"<audio_transcript>{transcript}"
    else:
        content = msg.text or ""
    with open(RECV_LOG, "a+", encoding="utf-8") as f:
        f.write(f"{ts},{content}\n")
    print("Registrado:", ts, content)

def scan_chats():
    if not driver.session_id:
        raise RuntimeError("Sessão inválida durante scan_chats")
    chats = driver.find_elements(By.XPATH, "//div[@id='pane-side']//div[contains(@class,'_2wP_Y')]")
    for c in chats[:5]:
        c.click()
        time.sleep(3)
        msgs = driver.find_elements(By.XPATH, "//div[contains(@class,'message-in')]")
        for msg in msgs[-10:]:
            ts = msg.get_attribute("data-pre-plain-text")
            process_message(msg, ts)

try:
    while True:
        scan_chats()
        time.sleep(60)
except Exception as e:
    print("Erro no listener_transcriber:", e)
finally:
    driver.quit()
