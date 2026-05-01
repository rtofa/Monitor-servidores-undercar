import os
import pytest
from playwright.sync_api import Page, expect
from app.core.config import settings

# --- FIXTURE ---
# Prepara a pasta temporária antes dos testes rodarem
@pytest.fixture(autouse=True)
def setup_teardown():
    os.makedirs("temp", exist_ok=True)
    yield

# --- TESTE 1: Validação do Login ---
def test_grafana_login_com_sucesso(page: Page):
    """Verifica se as credenciais funcionam e se a página inicial do Grafana é carregada."""
    
    # 1. Acessa a página
    page.goto(settings.grafana_url_login)
    
    # 2. Preenche o formulário
    page.fill("input[name='user']", settings.grafana_user)
    page.fill("input[name='password']", settings.grafana_password)
    page.keyboard.press("Enter")
    
    # 3. Validação (Assert): Aguarda a rede acalmar e verifica se a URL mudou (saiu do /login)
    page.wait_for_load_state("networkidle")
    assert "login" not in page.url, "O login falhou. A aplicação ainda está na tela de login."

# --- TESTE 2: Validação da Captura do Print ---
def test_captura_de_print_screen(page: Page):
    """Verifica se o navegador consegue acessar o dashboard e salvar o arquivo .png físico."""
    
    # Contexto: Faz o login rápido primeiro (Pré-requisito)
    page.goto(settings.grafana_url_login)
    page.fill("input[name='user']", settings.grafana_user)
    page.fill("input[name='password']", settings.grafana_password)
    page.keyboard.press("Enter")
    page.wait_for_load_state("networkidle")
    
    # 1. Acessa o Dashboard
    page.goto(settings.grafana_url_dashboard)
    
    # 2. Aguarda os componentes visuais renderizarem
    page.wait_for_timeout(3000)
    
    # 3. Define o caminho do arquivo de teste e tira o print
    caminho_teste = "temp/teste_screenshot.png"
    
    # Remove arquivo de teste antigo, se existir
    if os.path.exists(caminho_teste):
        os.remove(caminho_teste)
        
    page.screenshot(path=caminho_teste)
    
    # 4. Validação (Assert): Verifica se o arquivo foi CRIADO no sistema operacional
    assert os.path.exists(caminho_teste), "O arquivo de imagem não foi salvo no disco."
    
    # 5. Validação (Assert): Verifica se o arquivo NÃO ESTÁ VAZIO (tamanho maior que 0 bytes)
    tamanho_arquivo = os.path.getsize(caminho_teste)
    assert tamanho_arquivo > 0, f"A imagem foi salva, mas está vazia ({tamanho_arquivo} bytes)."
    
    # Limpeza após o teste passar
    os.remove(caminho_teste)