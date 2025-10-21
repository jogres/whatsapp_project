import os
import subprocess
import threading
from nicegui import ui
from dotenv import load_dotenv



load_dotenv()
LOG = 'data/system.log'
os.makedirs('data', exist_ok=True)
open(LOG, 'a').close()

proc = None
lock = threading.Lock()

def run_script(script, message=None, link=None):
    global proc
    with lock:
        if proc and proc.poll() is None:
            ui.notify('Já há um script em execução', position='top')
            return
        env = os.environ.copy()
        if message is not None:
            env['MSG_TEMPLATE'] = message
        if link is not None:
            env['MSG_LINK'] = link
        
        # Abrir logs com encoding UTF-8
        stdout_file = open(LOG, 'a', encoding='utf-8')
        stderr_file = open(LOG, 'a', encoding='utf-8')
        
        proc = subprocess.Popen(['python', script],
                                stdout=stdout_file,
                                stderr=stderr_file,
                                env=env)
        ui.notify(f'🤖 Rodando {script}', position='top')

def stop_script():
    global proc
    with lock:
        if proc and proc.poll() is None:
            proc.terminate()
            ui.notify('Script interrompido', position='top')
        else:
            ui.notify('Nenhum script em execução', position='top')

@ui.page('/')
def main_page():
    ui.label('💬 Painel Bot WhatsApp').classes('text-h4')

    # Estilo customizado para textarea alta
    ui.add_head_html('<style>.large-textarea .q-field__control { height: 200px; }</style>')

    message_input = ui.textarea(
        'Mensagem (use {nome})',
        placeholder='Olá {nome}, tudo bem?'
    ).classes('w-full large-textarea').props('size=120')  # largura ~120 caracteres, altura definida por CSS

    link_input = ui.input(
        'Link adicional (opcional)',
        placeholder='https://...'
    ).classes('w-full').props('size=120')  # largura ~120 caracteres

    with ui.row():
        ui.button('Enviar Mensagens',
                  on_click=lambda: run_script('sender.py', message_input.value, link_input.value))
        ui.button('Escutar + Transcrever',
                  on_click=lambda: run_script('listener_transcriber.py'))
        ui.button('Processar IA',
                  on_click=lambda: run_script('ai_process.py'))
        ui.button('Parar Script', on_click=stop_script)

    ui.separator()
    log_widget = ui.log(max_lines=200).classes('w-full h-96')
    
    def update_log():
        try:
            with open(LOG, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()[-200:]
                log_widget.set(lines)
        except Exception as e:
            log_widget.set([f"Erro ao ler log: {e}"])
    
    ui.timer(1.0, update_log)

ui.run(title='Bot WhatsApp', host='0.0.0.0', port=8080)

