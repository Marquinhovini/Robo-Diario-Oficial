import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
import pyautogui
import re

# Inicializando o navegador usando o Selenium
driver = webdriver.Chrome()  # Certifique-se de ter o WebDriver do Chrome configurado
driver.maximize_window()

# Abrindo o link
driver.get("https://diariooficial.jaboatao.pe.gov.br/")

# Aguardando a página carregar completamente (você pode ajustar este tempo conforme necessário)
time.sleep(2)

# Localizando o botão de pesquisa e clicando nele usando XPATH
pesquisa_button = driver.find_element(By.XPATH, '/html/body/div[1]/section[3]/div/div[2]/div/div/div/search/form/div[1]/i')
pesquisa_button.click()

# Esperando um pouco antes de usar o PyAutoGUI (opcional)
time.sleep(1)

# Usando o PyAutoGUI para preencher o campo de pesquisa e pressionar Enter
pyautogui.write("Exonerar")
pyautogui.press('enter')

# Aguardando a página carregar novamente após a pesquisa (ajuste conforme necessário)
time.sleep(2)
# Loop para percorrer todas as páginas de resultados
while True:
# Coletando os links dos resultados de pesquisa
    link_elements = driver.find_elements(By.XPATH, '//*[@id="post-46138"]/div/header/h2/a | //*[@id="post-46124"]/div/header/h2/a | //*[@id="post-46071"]/div/header/h2/a | //*[@id="post-46018"]/div/header/h2/a | //*[@id="post-45979"]/div/header/h2/a | //*[@id="post-45935"]/div/header/h2/a | //*[@id="post-45887"]/div/header/h2/a | //*[@id="post-45845"]/div/header/h2/a | //*[@id="post-45811"]/div/header/h2/a | //*[@id="post-45791"]/div/header/h2/a')

    num_links = min(len(link_elements), 10)  # Limitando a 10 links

    dados = []

    # Iterando sobre os links e coletando informações
    for link_element in link_elements:
        link = link_element.get_attribute("href")
        driver.execute_script("window.open('" + link + "');")  # Abrindo o link em uma nova aba
        driver.switch_to.window(driver.window_handles[-1])  # Mudando para a nova aba

        # Coletando informações de texto da página
        texto = driver.find_element(By.XPATH, '//*[@id="textointerno"]').text
        

        # Extraindo informações relevantes (nome e matrícula)
        matches = re.findall(r"EXONERAR.*?(\b[A-Z\s]+\b),\s+matrícula\s+nº\s+([\d.-]+)|<strong>\s*([^<]+)\s*<\/strong>\s*matrícula\s+nº\s*<strong>([\d.]+)<\/strong>", texto)

        for match in matches:
            if match[0]:
                nome = match[0].strip()
                matricula = match[1].strip()
            else:
                nome = match[2].strip()
                matricula = match[3].strip()
        
            print("Nome:", nome)
            print("Matrícula:", matricula)
            dados.append([nome, matricula])

        time.sleep(2)
        driver.close()  # Fechando a aba atual
        driver.switch_to.window(driver.window_handles[0])  # Mudando de volta para a primeira aba

    # Navegando para a próxima página de resultados
    next_button = driver.find_element(By.XPATH, '//*[@id="nav-below"]/div[2]/a[3]')
    next_button.click()

    # Fechando o navegador
    driver.quit()

    # Escrevendo os dados coletados em um arquivo CSV
    if dados:
        with open('dados_exoneracao.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Nome", "Matricula"])
            writer.writerows(dados)
    else:
        print("NHM DADOS")
