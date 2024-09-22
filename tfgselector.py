import json
from time import sleep

from alive_progress import alive_it
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from questionary import confirm, select
from selenium.webdriver.support.ui import Select


def filter_by(driver: WebDriver, selector_wrapper: WebElement):
    # Get options inside the selector inside the selector wrapper
    selector = selector_wrapper.find_element(By.TAG_NAME, 'select')
    options = selector.find_elements(By.TAG_NAME, 'option')

    # Let the user choose an option
    selected = select(
        "Selecciona una opción",
        [option.text for option in options if option.text != '']
    ).ask()

    # Select the option
    selector = Select(selector)
    selector.select_by_visible_text(selected)


def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    driver.implicitly_wait(3)
    driver.get("https://tfc.eii.us.es/TFG/")

    titulacion_selector = driver.find_element(By.ID, 'gwt-uid-3')
    seccion_selector = driver.find_element(By.ID, 'gwt-uid-5')
    departamento_selector = driver.find_element(By.ID, 'gwt-uid-7')
    profesor_selector = driver.find_element(By.ID, 'gwt-uid-9')

    filter_by(driver, titulacion_selector)

    if confirm("¿Quieres filtrar por sección?").ask():
        filter_by(driver, seccion_selector)

    if confirm("¿Quieres filtrar por departamento?").ask():
        filter_by(driver, departamento_selector)

    if confirm("¿Quieres filtrar por profesor?").ask():
        filter_by(driver, profesor_selector)

    # Click on the search button
    driver.find_element(By.XPATH, '//span[text()="Buscar"]').click()

    # Wait for the results to load
    sleep(5)

    # Get the results
    propuestas = []
    results = driver.find_elements(By.CLASS_NAME, "v-slot-v-propuesta")
    print(f'{len(results)} propuestas encontradas')
    for result in alive_it(results):
        propuesta = dict()
        propuesta['ref'] = result.find_element(By.CLASS_NAME, 'v-panel-caption-v-propuesta').text.split('[Ref.: ')[1].split('] - ')[0]
        propuesta['titulo'] = result.find_element(By.CLASS_NAME, 'v-panel-caption-v-propuesta').text.split('] - ')[-1]

        propuesta['descripcion'] = result.find_element(By.XPATH, ".//span[text()='Descripción:']/ancestor::div/following-sibling::textarea").get_attribute('value')

        try:
            propuesta['objetivos'] = result.find_element(By.XPATH, ".//span[text()='Objetivos:']/ancestor::div/following-sibling::textarea").get_attribute('value')
        except:
            propuesta['objetivos'] = ''

        try:
            propuesta['tecnologias'] = result.find_element(By.XPATH, ".//span[text()='Tecnologías:']/ancestor::div/following-sibling::textarea").get_attribute('value')
        except:
            propuesta['tecnologias'] = ''

        try:
            propuesta['requistos'] = result.find_element(By.XPATH, ".//span[text()='Requisitos:']/ancestor::div/following-sibling::textarea").get_attribute('value')
        except:
            propuesta['requistos'] = ''

        try:
            propuesta['grupo'] = result.find_element(By.XPATH, ".//span[text()='Grupo:']/ancestor::div/following-sibling::textarea").get_attribute('value') == 'Sí'
        except:
            propuesta['grupo'] = False

        result.find_element(By.CSS_SELECTOR, '.v-button-caption').click()
        propuesta['profesor'] = dict()
        propuesta['profesor']['nombre'] = driver.find_element(By.XPATH, "//span[text()='Nombre:']/ancestor::div/following-sibling::input").get_attribute('value')
        propuesta['profesor']['departamento'] = driver.find_element(By.XPATH, "//span[text()='Departamento:']/ancestor::div/following-sibling::input").get_attribute('value')
        propuesta['profesor']['email'] = driver.find_element(By.XPATH, "//span[text()='Email:']/ancestor::div/following-sibling::input").get_attribute('value')
        propuesta['profesor']['despacho'] = driver.find_element(By.XPATH, "//span[text()='Despacho:']/ancestor::div/following-sibling::input").get_attribute('value')
        driver.find_element(By.XPATH, "//span[text()=' Cerrar']").click()

        propuestas.append(propuesta)

    # Exports the data to JSON
    with open('propuestas.json', 'w', encoding='utf-8') as f:
        json.dump(propuestas, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
