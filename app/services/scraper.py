import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from app.core.config import settings

def verificar_servidores() -> tuple[str | None, bool, list]:
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_imagem = os.path.join(temp_dir, f"status_{timestamp}.png")

    with sync_playwright() as p:
        # 1. AUMENTAMOS O MONITOR: 1920x1080 garante que ele veja mais coisas
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True, viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            # Login
            page.goto(settings.grafana_url_login)
            page.fill("input[name='user']", settings.grafana_user)
            page.fill("input[name='password']", settings.grafana_password)
            page.keyboard.press("Enter")
            page.wait_for_load_state("networkidle")

            # Acessa o Dashboard
            page.goto(settings.grafana_url_dashboard)
            
            # Aguarda os blocos superiores carregarem
            page.wait_for_timeout(3000) 

            # 2. O TRUQUE CONTRA O LAZY LOADING: Força o scroll até o final da página
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Aguarda a tabela inferior puxar os dados do banco de dados (3 segundos)
            page.wait_for_timeout(3000)

            # Lendo a Tabela de Problemas
            servidores_com_erro = page.evaluate(r"""() => {
                let falhas = new Set();
                const linhas = document.querySelectorAll('tr, [role="row"], div[class*="table-row"]');

                linhas.forEach(linha => {
                    const textoLinha = (linha.innerText || linha.textContent).toUpperCase();
                    
                    // Adicionei 'HIGH' como garantia extra, já que está na coluna Severity
                    if (textoLinha.includes('PROBLEM') || textoLinha.includes('OFF-LINE') || textoLinha.includes('HIGH')) {
                        
                        const celulas = linha.querySelectorAll('td, [role="gridcell"], .table-panel-cell, div[class*="table-cell"]');
                        
                        if (celulas.length > 0) {
                            const nomeServidor = celulas[0].innerText.trim();
                            if (nomeServidor && nomeServidor.toUpperCase() !== 'HOST') {
                                falhas.add(nomeServidor);
                            }
                        } else {
                            const pedacos = (linha.innerText || "").split('\n').map(t => t.trim()).filter(t => t.length > 0);
                            if (pedacos.length > 0 && pedacos[0].toUpperCase() !== 'HOST') {
                                falhas.add(pedacos[0]);
                            }
                        }
                    }
                });

                return Array.from(falhas);
            }""")

            # 3. PRINT COMPLETO: Agora a foto sai comprida, mostrando os blocos e a tabela de erros embaixo
            page.screenshot(path=caminho_imagem, full_page=True)

            tem_erro = len(servidores_com_erro) > 0

            return caminho_imagem, tem_erro, servidores_com_erro
            
        except Exception as e:
            print(f"Falha na extração com Playwright: {e}")
            return None, True, ["Erro de Conexão com Grafana"]
        finally:
            browser.close()