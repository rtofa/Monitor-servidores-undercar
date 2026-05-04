import os
from playwright.sync_api import sync_playwright

def tirar_print_para_whatsapp():
    caminho_imagem = "temp/grafana_status.png"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True) 
        page = context.new_page()

        try:
            # Faz o login obrigatório
            page.goto("https://grafana.example.com/login")
            page.fill("input[name='user']", "REDACTED_EMAIL")
            page.fill("input[name='password']", "REDACTED_PASSWORD")
            page.keyboard.press("Enter")
            page.wait_for_url("**/d/**")
            
            # Acessa o grid geral e tira a foto
            page.goto("https://grafana.example.com/d/UID/dashboard?orgId=1", wait_until="networkidle")
            page.wait_for_timeout(4000)
            
            os.makedirs("temp", exist_ok=True)
            page.screenshot(path=caminho_imagem, full_page=True)

        except Exception as e:
            print(f"Erro ao tirar print: {e}")
            return None
        finally:
            browser.close()

    return caminho_imagem