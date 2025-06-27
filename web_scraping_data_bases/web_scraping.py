from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import chromedriver_autoinstaller
import time
import csv

# Instala e configura o ChromeDriver automaticamente
chromedriver_autoinstaller.install()
options = Options()
options.add_argument("--start-maximized")

# Funções de extração de dados
def extrair_titulo(bloco):
    # Tenta primeiro pelo data-testid
    try:
        return bloco.find_element(By.CSS_SELECTOR, '[data-testid="review-title"]').text.strip()
    except:
        pass
    # Tenta por tags mais genéricas (caso não tenha data-testid)
    for seletor in ['h3', 'h4', 'div']:
        try:
            return bloco.find_element(By.CSS_SELECTOR, seletor).text.strip()
        except:
            continue
    return ""

def extrair_nota(bloco):
    # Tenta por data-testid com classe mais específica
    try:
        nota_elemento = bloco.find_element(By.CSS_SELECTOR, '[data-testid="review-score"] div.a3b8729ab1')
        return nota_elemento.text.strip().split('\n')[-1]
    except:
        pass
    # Tenta por XPath mais genérico
    try:
        nota = bloco.find_element(By.XPATH, ".//div[contains(text(), 'Com nota')]").text.strip().split('\n')[-1]
        return nota
    except:
        pass
    return ""

# Inicia o navegador
driver = webdriver.Chrome(options=options)
driver.get("https://www.booking.com/hotel/br/beach-class-suites.pt-br.html#tab-reviews")
time.sleep(5)  # Aguarda carregamento inicial

comentarios = []
pagina = 1  # Controlador de página

while True:
    print(f"🔄 Página {pagina}")

    time.sleep(3)

    # Scroll até o topo (gatilho de renderização)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

    # Espera carregar os elementos
    cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="review-card"]')

    for bloco in cards:
        try:
            data = bloco.find_element(By.CSS_SELECTOR, 'span[data-testid="review-date"]').text.replace("Avaliação: ", "")
        except:
            data = ""
        
        titulo = extrair_titulo(bloco)

        try:
            positivo = bloco.find_element(By.CSS_SELECTOR, 'div[data-testid="review-positive-text"] div.a53cbfa6de span').text
        except:
            positivo = ""

        try:
            negativo = bloco.find_element(By.CSS_SELECTOR, 'div[data-testid="review-negative-text"] div.a53cbfa6de span').text
        except:
            negativo = ""
        
        
        nota = extrair_nota(bloco)


        comentarios.append((data, titulo, positivo, negativo, nota))

    # Limite de páginas
    if pagina >= 201:
        print("⛔ Limite de páginas atingido.")
        break

    try:
        botao_proxima = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Página seguinte"]')
        driver.execute_script("arguments[0].scrollIntoView();", botao_proxima)
        time.sleep(1)
        botao_proxima.click()
        pagina += 1
        time.sleep(3)
    except:
        print("✅ Fim da paginação.")
        break

# Fecha navegador
driver.quit()

# Exportar CSV
arquivo_csv = "Radisson_Recife.csv"
# Exportar CSV com proteção contra quebras e vírgulas
with open(arquivo_csv, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL, quotechar='"')
    writer.writerow(["data_avaliacao", "titulo", "comentario_positivo", "comentario_negativo", "nota"])
    writer.writerows(comentarios)

print(f"\n📁 CSV gerado com sucesso: {arquivo_csv}")
print(f"🧾 Total de comentários salvos: {len(comentarios)}")