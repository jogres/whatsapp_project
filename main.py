import os
import sys
import subprocess
import threading
import pandas as pd
from nicegui import ui

# Tornar o sistema portável - usar caminhos relativos ao script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(SCRIPT_DIR, 'data', 'system.log')
SENT_LOG = os.path.join(SCRIPT_DIR, 'data', 'sent_log.csv')
CONTATOS_FILE = os.path.join(SCRIPT_DIR, 'data', 'contatos.xlsx')
os.makedirs(os.path.join(SCRIPT_DIR, 'data'), exist_ok=True)
open(LOG, 'a').close()

proc = None
lock = threading.Lock()

def get_stats():
    """Obtém estatísticas dos envios"""
    stats = {'total': 0, 'enviados': 0}
    try:
        if os.path.exists(CONTATOS_FILE):
            df = pd.read_excel(CONTATOS_FILE, dtype=str)
            stats['total'] = len(df)
        
        if os.path.exists(SENT_LOG):
            with open(SENT_LOG, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                stats['enviados'] = len([l for l in lines if l.strip()])
    except:
        pass
    return stats

def run_script(script, message=None, link=None, use_profile=False):
    global proc
    with lock:
        if proc and proc.poll() is None:
            ui.notify('⚠️ Já há um script em execução!', type='warning', position='top')
            return
        
        # Validar mensagem
        if not message or not message.strip():
            ui.notify('❌ Digite uma mensagem antes de iniciar!', type='negative', position='top')
            return
        
        # Validar arquivo de contatos
        if not os.path.exists(CONTATOS_FILE):
            ui.notify(f'❌ Arquivo {CONTATOS_FILE} não encontrado!', type='negative', position='top')
            return
        
        # Usar caminho absoluto do script para portabilidade
        script_path = os.path.join(SCRIPT_DIR, script)
        if not os.path.exists(script_path):
            ui.notify(f'❌ Script {script} não encontrado!', type='negative', position='top')
            return
        
        env = os.environ.copy()
        if message is not None:
            env['MSG_TEMPLATE'] = message
        if link is not None:
            env['MSG_LINK'] = link
        env['USE_PROFILE'] = 'true' if use_profile else 'false'
        
        # Configurar encoding UTF-8 para o subprocess no Windows
        if sys.platform == 'win32':
            env['PYTHONIOENCODING'] = 'utf-8'
        
        stdout_file = open(LOG, 'a', encoding='utf-8', errors='replace')
        stderr_file = open(LOG, 'a', encoding='utf-8', errors='replace')
        
        # Usar caminho absoluto do Python e do script para portabilidade
        python_exe = sys.executable
        # Não usar CREATE_NO_WINDOW - o Chrome precisa estar visível para login
        proc = subprocess.Popen([python_exe, script_path],
                                stdout=stdout_file,
                                stderr=stderr_file,
                                env=env,
                                cwd=SCRIPT_DIR)
        ui.notify('🚀 Envio iniciado com sucesso!', type='positive', position='top', timeout=3000)

def stop_script():
    global proc
    with lock:
        if proc and proc.poll() is None:
            proc.terminate()
            ui.notify('⏹️ Script interrompido', type='info', position='top')
        else:
            ui.notify('ℹ️ Nenhum script em execução', type='info', position='top')

@ui.page('/')
def main_page():
    # CSS moderno e responsivo
    ui.add_head_html('''
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            background-attachment: fixed;
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0;
            padding: 0;
        }
        .main-wrapper {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            min-height: 100vh;
        }
        .header-section {
            background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
            color: white;
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-box {
            background: white;
            border-radius: 16px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border-left: 4px solid;
        }
        .stat-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        .stat-box.total { border-left-color: #2196F3; }
        .stat-box.enviados { border-left-color: #4CAF50; }
        .stat-box.pendentes { border-left-color: #FF9800; }
        .stat-box.erros { border-left-color: #F44336; }
        .stat-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .stat-number {
            font-size: 3em;
            font-weight: 700;
            margin: 10px 0;
            color: #333;
        }
        .stat-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .content-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        @media (max-width: 968px) {
            .content-grid {
                grid-template-columns: 1fr;
            }
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        .card:hover {
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        .card-title {
            font-size: 1.4em;
            font-weight: 700;
            margin-bottom: 20px;
            color: #333;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .btn-large {
            padding: 15px 40px;
            font-size: 1.1em;
            font-weight: 600;
            border-radius: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        .btn-large:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }
        .status-badge {
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.95em;
        }
        .status-running {
            background: #E8F5E9;
            color: #2E7D32;
        }
        .status-waiting {
            background: #F5F5F5;
            color: #616161;
        }
        .log-viewer {
            background: #1e1e1e;
            color: #d4d4d4;
            border-radius: 12px;
            padding: 20px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            max-height: 450px;
            overflow-y: auto;
            line-height: 1.6;
        }
        .log-viewer::-webkit-scrollbar {
            width: 8px;
        }
        .log-viewer::-webkit-scrollbar-track {
            background: #2d2d2d;
            border-radius: 4px;
        }
        .log-viewer::-webkit-scrollbar-thumb {
            background: #555;
            border-radius: 4px;
        }
        .log-viewer::-webkit-scrollbar-thumb:hover {
            background: #777;
        }
        .input-field {
            margin-bottom: 20px;
        }
        .help-section {
            background: #F5F5F5;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
        }
        .quick-info {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px;
            background: #E3F2FD;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #2196F3;
        }
        .progress-indicator {
            height: 4px;
            background: #E0E0E0;
            border-radius: 2px;
            overflow: hidden;
            margin: 15px 0;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            transition: width 0.3s ease;
        }
    </style>
    ''')
    
    with ui.column().classes('main-wrapper'):
        # Header Principal
        with ui.column().classes('header-section'):
            ui.icon('whatsapp', size='64px').classes('mb-4')
            ui.label('Bot WhatsApp').classes('text-h2 font-bold mb-2')
            ui.label('Sistema de Envio em Massa').classes('text-h6 opacity-90')
        
        # Estatísticas - Grid Responsivo
        stats = {'total': 0, 'enviados': 0, 'erros': 0}
        stats.update(get_stats())
        
        with ui.row().classes('stats-grid w-full'):
            # Total de Contatos
            with ui.card().classes('stat-box total'):
                ui.label('👥').classes('stat-icon')
                total_label = ui.label(str(stats['total'])).classes('stat-number')
                ui.label('Total de Contatos').classes('stat-label')
            
            # Enviados
            with ui.card().classes('stat-box enviados'):
                ui.label('✅').classes('stat-icon')
                enviados_label = ui.label(str(stats['enviados'])).classes('stat-number')
                ui.label('Enviados').classes('stat-label')
            
            # Pendentes
            pendentes = max(0, stats['total'] - stats['enviados'])
            with ui.card().classes('stat-box pendentes'):
                ui.label('⏳').classes('stat-icon')
                pendentes_label = ui.label(str(pendentes)).classes('stat-number')
                ui.label('Pendentes').classes('stat-label')
            
            # Taxa de Sucesso
            taxa = (stats['enviados'] / stats['total'] * 100) if stats['total'] > 0 else 0
            with ui.card().classes('stat-box enviados'):
                ui.label('📊').classes('stat-icon')
                taxa_label = ui.label(f'{taxa:.1f}%').classes('stat-number')
                ui.label('Taxa de Sucesso').classes('stat-label')
        
        # Grid Principal - Configuração e Controles lado a lado
        with ui.row().classes('content-grid w-full'):
            # Coluna Esquerda - Configuração
            with ui.column().classes('w-full'):
                with ui.card():
                    ui.label('⚙️ Configuração').classes('card-title')
                    
                    message_input = ui.textarea(
                        label='Mensagem',
                        placeholder='Digite sua mensagem aqui...\n\nUse {nome} para personalizar para cada contato.\nExemplo: Olá {nome}, tudo bem?',
                        value='Olá {nome}, tudo bem?'
                    ).classes('input-field w-full').props('rows=6 outlined autogrow')
                    
                    link_input = ui.input(
                        label='Link Adicional (Opcional)',
                        placeholder='https://exemplo.com'
                    ).classes('input-field w-full').props('outlined clearable')
                    
                    # Informações rápidas
                    with ui.column().classes('w-full mt-4'):
                        with ui.row().classes('quick-info'):
                            ui.icon('info', size='20px').classes('text-blue-600')
                            ui.label('Use {nome} no template para personalizar cada mensagem').classes('text-sm')
                        
                        with ui.row().classes('quick-info'):
                            ui.icon('link', size='20px').classes('text-blue-600')
                            ui.label('O link será adicionado automaticamente ao final da mensagem').classes('text-sm')
            
            # Coluna Direita - Controles e Status
            with ui.column().classes('w-full'):
                with ui.card():
                    ui.label('🎮 Controles').classes('card-title')
                    
                    # Status atual
                    status_badge = ui.label('⏸️ Aguardando').classes('status-badge status-waiting mb-4')
                    
                    # Barra de progresso
                    progress_container = ui.column().classes('w-full mb-4')
                    with progress_container:
                        progress_text = ui.label('0% (0/0)').classes('text-center text-sm text-grey-600 mb-2')
                        progress_bar = ui.linear_progress(value=0).classes('w-full').props('show-value=false')
                    
                    # Botões de ação
                    with ui.row().classes('w-full gap-3 justify-center'):
                        start_btn = ui.button(
                            '🚀 Iniciar Envio',
                            on_click=lambda: run_script('sender.py', message_input.value, link_input.value, use_profile_switch.value)
                        ).classes('btn-large').props('color=primary size=lg')
                        
                        stop_btn = ui.button(
                            '⏹️ Parar',
                            on_click=stop_script
                        ).classes('btn-large').props('color=negative size=lg')
                    
                    # Opção de perfil persistente
                    use_profile_switch = ui.switch('💾 Usar perfil persistente (salva login)', value=False).classes('w-full mt-4')
                    ui.label('Desligado = Login toda vez (portável) | Ligado = Salva login').classes('text-xs text-grey-600 mb-2')
                    
                    # Informações do arquivo
                    with ui.column().classes('w-full mt-4'):
                        ui.separator()
                        file_name = os.path.basename(CONTATOS_FILE)
                        file_info = ui.label(f'📄 Arquivo: {file_name}').classes('text-sm text-grey-600 mt-2')
                        if os.path.exists(CONTATOS_FILE):
                            try:
                                df = pd.read_excel(CONTATOS_FILE, dtype=str)
                                file_info.text = f'📄 Arquivo: {file_name} ({len(df)} contatos)'
                            except:
                                pass
        
        # Logs - Tela cheia
        with ui.card().classes('w-full'):
            with ui.row().classes('w-full items-center justify-between mb-4'):
                ui.label('📊 Logs em Tempo Real').classes('card-title')
                status_label = ui.label('⏸️ Aguardando...').classes('status-badge status-waiting')
            
            log_widget = ui.log(max_lines=150).classes('log-viewer w-full')
            
            def update_log():
                try:
                    # Atualizar status
                    global proc
                    is_running = False
                    with lock:
                        if proc and proc.poll() is None:
                            is_running = True
                    
                    if is_running:
                        status_badge.text = '🟢 Em Execução'
                        status_badge.style('background: #E8F5E9; color: #2E7D32; padding: 8px 20px; border-radius: 20px; font-weight: 600;')
                        status_label.text = '🟢 Em Execução'
                        status_label.style('background: #E8F5E9; color: #2E7D32; padding: 8px 20px; border-radius: 20px; font-weight: 600;')
                        start_btn.props('disabled')
                    else:
                        status_badge.text = '⏸️ Aguardando'
                        status_badge.style('background: #F5F5F5; color: #616161; padding: 8px 20px; border-radius: 20px; font-weight: 600;')
                        status_label.text = '⏸️ Aguardando'
                        status_label.style('background: #F5F5F5; color: #616161; padding: 8px 20px; border-radius: 20px; font-weight: 600;')
                        start_btn.props(remove='disabled')
                    
                    # Atualizar logs
                    with open(LOG, 'r', encoding='utf-8') as f:
                        lines = f.read().splitlines()[-150:]
                        log_widget.set(lines)
                    
                    # Atualizar estatísticas e progresso
                    new_stats = get_stats()
                    if new_stats['enviados'] != stats['enviados'] or new_stats['total'] != stats['total']:
                        stats['enviados'] = new_stats['enviados']
                        stats['total'] = new_stats['total']
                        enviados_label.text = str(stats['enviados'])
                        pendentes_label.text = str(max(0, stats['total'] - stats['enviados']))
                        
                        # Atualizar progresso
                        if stats['total'] > 0:
                            progress = (stats['enviados'] / stats['total']) * 100
                            progress_bar.value = progress / 100
                            progress_text.text = f'{progress:.1f}% ({stats["enviados"]}/{stats["total"]})'
                            taxa_label.text = f'{progress:.1f}%'
                except Exception as e:
                    pass
            
            ui.timer(0.5, update_log)
        
        # Ajuda Rápida - Colapsável
        with ui.card().classes('w-full'):
            with ui.expansion('❓ Ajuda Rápida', icon='help').classes('w-full'):
                with ui.column().classes('help-section'):
                    ui.markdown('''
                    ### 📋 Passo a Passo:
                    
                    1. **Prepare o Excel**: Crie `data/contatos.xlsx` com colunas `nome` e `telefone`
                    2. **Configure**: Digite sua mensagem (use `{nome}` para personalizar)
                    3. **Envie**: Clique em "Iniciar Envio" e acompanhe o progresso
                    
                    ### 💡 Dicas:
                    - O primeiro uso requer login manual no WhatsApp Web
                    - Use com moderação para evitar bloqueios
                    - Os logs mostram o progresso em tempo real
                    - Você pode parar o envio a qualquer momento
                    
                    ### 📁 Arquivos:
                    - `data/contatos.xlsx` - Lista de contatos
                    - `data/sent_log.csv` - Histórico de envios
                    - `data/system.log` - Logs do sistema
                    ''')
        
        # Footer
        with ui.row().classes('w-full justify-center mt-6 mb-4'):
            ui.label('Desenvolvido com ❤️ | Python + Selenium + NiceGUI').classes('text-caption text-white opacity-80')

ui.run(title='Bot WhatsApp - Envio em Massa', host='0.0.0.0', port=8080, favicon='📱', dark=False)
