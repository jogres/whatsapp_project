import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
AI_ENDPOINT = os.getenv("AI_ENDPOINT")
API_KEY = os.getenv("OPENAI_API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

RECV_LOG = os.path.join(os.path.abspath("data"), "received_log.csv")
if not os.path.exists(RECV_LOG):
    print("received_log.csv não encontrado")
else:
    df = pd.read_csv(RECV_LOG, names=["timestamp","content"], dtype=str)

    for _, row in df.iterrows():
        is_audio = row["content"].startswith("<audio_transcript>")
        content = row["content"].replace("<audio_transcript>","") if is_audio else row["content"]
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Você é um assistente que analisa mensagens recebidas, de forma a entender o contexto e fornecer respostas relevantes e como melhorar a comunicação para que seja mais eficaz e natural gerando uma venda."},
                {"role": "user", "content": content}
            ]
        }
        resp = requests.post(AI_ENDPOINT, headers=HEADERS, json=payload)
        if resp.ok:
            reply = resp.json()["choices"][0]["message"]["content"]
            print(f"[{'audio' if is_audio else 'text'}] IA respondeu:", reply)
        else:
            print("Erro IA:", resp.status_code, resp.text)
