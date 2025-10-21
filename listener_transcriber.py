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
opts.add_experimental_option("prefs", {
    "download.default_directory": DATA_DIR,
    "download.prompt_for_download": False,
})

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
    
    # Verificar se é mensagem de áudio
    audio_elements = msg.find_elements(By.TAG_NAME, "audio")
    if audio_elements:
        try:
            # Clicar no menu da mensagem
            menu_btn = msg.find_element(By.XPATH, ".//span[@data-icon='menu']")
            ActionChains(driver).move_to_element(menu_btn).click().perform()
            time.sleep(1)
            
            # Clicar em download
            download_btn = driver.find_element(By.XPATH, "//li[@data-testid='download']")
            download_btn.click()
            time.sleep(5)
            
            transcript = ""
            # Buscar arquivos de áudio baixados
            download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            audio_patterns = [
                os.path.join(download_folder, "*.ogg"),
                os.path.join(download_folder, "*.mp3"),
                os.path.join(download_folder, "*.opus"),
                os.path.join(DATA_DIR, "*.ogg"),
                os.path.join(DATA_DIR, "*.mp3"),
                os.path.join(DATA_DIR, "*.opus")
            ]
            
            files = []
            for pattern in audio_patterns:
                files.extend(glob.glob(pattern))
            
            if files:
                # Pegar o arquivo mais recente
                path = max(files, key=os.path.getmtime)
                
                try:
                    with AudioFile(path) as src:
                        audio = recognizer.record(src)
                        transcript = recognizer.recognize_google(audio, language="pt-BR")
                except Exception as e:
                    transcript = f"<erro_transcricao:{str(e)}>"
                    print(f"Erro na transcrição: {e}")
                
                # Remover arquivo após processar
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Erro ao remover arquivo {path}: {e}")
            else:
                transcript = "<erro:arquivo_nao_encontrado>"
                
            content = f"<audio_transcript>{transcript}"
        except Exception as e:
            print(f"Erro ao processar áudio: {e}")
            content = f"<audio_erro:{str(e)}>"
    else:
        # Mensagem de texto
        content = msg.text or ""
    
    # Salvar no log
    with open(RECV_LOG, "a+", encoding="utf-8") as f:
        f.write(f"{ts},{content}\n")
    print("Registrado:", ts, content)

def scan_chats():
    if not driver.session_id:
        raise RuntimeError("Sessão inválida durante scan_chats")
    
    try:
        # Tentar encontrar chats - XPath pode mudar com atualizações do WhatsApp
        chats = driver.find_elements(By.XPATH, "//div[@id='pane-side']//div[contains(@class,'_2wP_Y')]")
        
        if not chats:
            print("Nenhum chat encontrado. O WhatsApp pode ter mudado a estrutura HTML.")
            return
        
        print(f"Encontrados {len(chats)} chats. Processando os primeiros 5...")
        
        for i, c in enumerate(chats[:5]):
            try:
                c.click()
                time.sleep(3)
                
                msgs = driver.find_elements(By.XPATH, "//div[contains(@class,'message-in')]")
                print(f"Chat {i+1}: {len(msgs)} mensagens encontradas")
                
                for msg in msgs[-10:]:
                    try:
                        ts = msg.get_attribute("data-pre-plain-text") or time.strftime("%Y-%m-%d %H:%M:%S")
                        process_message(msg, ts)
                    except Exception as e:
                        print(f"Erro ao processar mensagem: {e}")
                        
            except Exception as e:
                print(f"Erro ao processar chat {i+1}: {e}")
                continue
                
    except Exception as e:
        print(f"Erro geral no scan_chats: {e}")

try:
    while True:
        scan_chats()
        time.sleep(60)
except Exception as e:
    print("Erro no listener_transcriber:", e)
finally:
    driver.quit()
