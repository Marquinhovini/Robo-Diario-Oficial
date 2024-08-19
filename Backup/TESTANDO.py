import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

# Mapeamento de meses em inglês para português
meses = {
    'January': 'janeiro', 'February': 'fevereiro', 'March': 'março',
    'April': 'abril', 'May': 'maio', 'June': 'junho',
    'July': 'julho', 'August': 'agosto', 'September': 'setembro',
    'October': 'outubro', 'November': 'novembro', 'December': 'dezembro'
}

def coletar_dados_pagina(driver, data_atual_str):
    link_elements = driver.find_elements(By.XPATH, '//h2[@class="entry-title"]/a')
    dados_exonerar = []

    for link_element in link_elements:
        link = link_element.get_attribute("href")
        titulo = link_element.get_attribute("innerText")

        if data_atual_str.upper() in titulo.upper():
            driver.execute_script("window.open(arguments[0]);", link)
            driver.switch_to.window(driver.window_handles[-1])

            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="textointerno"]')))
                texto = driver.find_element(By.XPATH, '//*[@id="textointerno"]').text
                
                # Utilizamos expressão regular para capturar as informações de exoneração
                matches_exonerar = re.findall(r"EXONERAR\s+([\w\s]+?),\s+matrícula\s+n[°º]?\s+([\w\s°º.]+)", texto)

                for match in matches_exonerar:
                    nome = match[0]
                    matricula = match[1]
                    print("Nome:", nome, "matricula:", matricula, "Data:", data_atual_str_pt)
                    dados_exonerar.append((nome.strip(), matricula.strip(), data_atual_str_pt))
            except Exception as e:
                print(f"Erro ao coletar dados da página: {e}")

            time.sleep(2)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    return dados_exonerar

def converter_data(data, meses):
    dia, mes, ano = data.split()
    mes = meses[mes]
    return f"{dia} de {mes} de {ano}"

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://diariooficial.jaboatao.pe.gov.br/")
time.sleep(2)

pesquisa_button = driver.find_element(By.XPATH, '/html/body/div[1]/section[3]/div/div[2]/div/div/div/search/form/div[1]/i')
pesquisa_button.click()

data_inicial = input("Digite a data inicial (dd/mm/aaaa): ")
data_final = input("Digite a data final (dd/mm/aaaa): ")


data_final_obj = datetime.strptime(data_final, '%d/%m/%Y')
data_inicial_obj = datetime.strptime(data_inicial, '%d/%m/%Y')

dados_totais_exonerar = []

data_atual = data_inicial_obj
while data_atual <= data_final_obj:
    data_atual_str = data_atual.strftime('%d %B %Y')
    data_atual_str_pt = converter_data(data_atual_str, meses)
    print(f"Pesquisando por: {data_atual_str_pt}")



    try:
        # Voltar à página inicial e clicar na lupa antes de cada pesquisa
        driver.get("https://diariooficial.jaboatao.pe.gov.br/")
        pesquisa_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/section[3]/div/div[2]/div/div/div/search/form/div[1]/i'))
        )
        pesquisa_button.click()

        # Esperar o campo de pesquisa estar disponível
        elemento = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "elementor-search-form-1b38a33a"))
        )
        elemento.clear()
        elemento.send_keys(data_atual_str_pt)
        elemento.send_keys(Keys.ENTER)

        time.sleep(1)

        dados_pagina_exonerar = coletar_dados_pagina(driver, data_atual_str_pt)
        if dados_pagina_exonerar:
            dados_totais_exonerar.extend(dados_pagina_exonerar)
        else:
            print(f"Sem resultado de data para: {data_atual_str_pt}")
    except Exception as e:
        print(f"Erro ao pesquisar pela data {data_atual_str_pt}: {e}")

    data_atual += timedelta(days=1)

driver.quit()

if dados_totais_exonerar:
    with open('dados_exoneracao.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Nome", "Matricula", "Data"])
        writer.writerows(dados_totais_exonerar)
    print("Finalizado com sucesso")
else:
    print("Nenhum dado encontrado")

