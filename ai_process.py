import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

# Validar variáveis de ambiente
AI_ENDPOINT = os.getenv("AI_ENDPOINT", "https://api.openai.com/v1/chat/completions")
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("ERRO: OPENAI_API_KEY não configurada no arquivo .env")

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

RECV_LOG = os.path.join(os.path.abspath("data"), "received_log.csv")

print(f"Usando endpoint: {AI_ENDPOINT}")

if not os.path.exists(RECV_LOG):
    print(f"ERRO: {RECV_LOG} não encontrado. Execute o listener_transcriber.py primeiro.")
    exit(1)
else:
    try:
        df = pd.read_csv(RECV_LOG, names=["timestamp","content"], dtype=str)
    except Exception as e:
        print(f"ERRO ao ler CSV: {e}")
        exit(1)
    
    if df.empty:
        print("AVISO: O arquivo received_log.csv está vazio. Nenhuma mensagem para processar.")
        exit(0)
    
    print(f"Processando {len(df)} mensagens...\n")
    
    for idx, row in df.iterrows():
        try:
            # Verificar se o conteúdo existe
            if pd.isna(row["content"]) or not row["content"]:
                print(f"Linha {idx+1}: Conteúdo vazio, pulando...")
                continue
            
            is_audio = str(row["content"]).startswith("<audio_transcript>")
            content = str(row["content"]).replace("<audio_transcript>", "") if is_audio else str(row["content"])
            
            # Pular mensagens de erro
            if content.startswith("<erro") or content.startswith("<audio_erro"):
                print(f"Linha {idx+1}: Mensagem com erro, pulando...")
                continue
            
            print(f"\n{'='*60}")
            print(f"Processando mensagem {idx+1}/{len(df)} [{'ÁUDIO' if is_audio else 'TEXTO'}]")
            print(f"Conteúdo: {content[:100]}{'...' if len(content) > 100 else ''}")
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "Você é um assistente que analisa mensagens recebidas, de forma a entender o contexto e fornecer respostas relevantes e como melhorar a comunicação para que seja mais eficaz e natural gerando uma venda."},
                    {"role": "user", "content": content}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            try:
                resp = requests.post(AI_ENDPOINT, headers=HEADERS, json=payload, timeout=30)
                
                if resp.ok:
                    reply = resp.json()["choices"][0]["message"]["content"]
                    print(f"\n✅ Resposta da IA:")
                    print(f"{reply}")
                else:
                    print(f"\n❌ Erro na API (HTTP {resp.status_code}):")
                    print(f"{resp.text}")
                    
            except requests.exceptions.Timeout:
                print("❌ Timeout ao chamar a API (>30s)")
            except requests.exceptions.ConnectionError:
                print("❌ Erro de conexão com a API")
            except Exception as e:
                print(f"❌ Erro ao chamar API: {e}")
                
        except Exception as e:
            print(f"❌ Erro ao processar linha {idx+1}: {e}")
            continue
    
    print(f"\n{'='*60}")
    print("✅ Processamento concluído!")
