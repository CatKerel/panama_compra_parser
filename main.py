from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import pandas as pd
import sys
from bs4 import BeautifulSoup


def run_webdriver():
    # set options
    ops = webdriver.ChromeOptions()
    ops.add_argument("--headless")
    # ops.add_argument("--disable-blink-features=AutomationControlled")
    ops.add_argument("--window-size=1000x2000")
    ops.add_argument("start-maximised")
    # start webdriver
    wb = webdriver.Chrome(options=ops)
    # open website
    url = 'https://www.panamacompra.gob.pa/Inicio/#/cotizaciones-en-linea/cotizaciones-en-linea?q=eyJlc3RhZG8iOjUwfQ'
    wb.get(url)
    return wb


def get_table_head(wb):
    xp_table_head = '/html/body/app-root/main/ng-component/div/section[2]/ng-component/div/div[' \
                    '2]/tabla-busqueda-avanzada/div[1]/table/thead/tr '
    table_head = wb.find_element(by=By.XPATH, value=xp_table_head)
    columns = list()
    for col in table_head.find_elements(by=By.TAG_NAME, value='th'):
        if len(col.text):
            columns.append(col.text)
    return columns


def get_data_from_page(wb, data):
    xp_table = '/html/body/app-root/main/ng-component/div/section[2]/ng-component/div/div[' \
               '2]/tabla-busqueda-avanzada/div[1]/table '
    table = wb.find_element(by=By.XPATH, value=xp_table)
    columns = get_table_head(wb)
    # 3 sec!

    for row in table.find_elements(by=By.TAG_NAME, value='tr'):
        els = list()
        print(row.text)
        for el in row.find_elements(by=By.TAG_NAME, value='td'):
            pass
            # els.append(el.text)
        if len(els):
            data = pd.concat([data, pd.DataFrame(data=[els], columns=columns)], axis=0, ignore_index=True)
    return data


def get_data_from_page_html(wb, data):
    html = wb.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_="table caption-top table-hover")
    rows = table.find_all('tr')
    columns = get_table_head(wb)
    for row in rows:
        els = row.find_all('td')
        els_list = list()
        for el in els:
            els_list.append(el.text)
        if len(els_list):
            data = pd.concat([data, pd.DataFrame(data=[els_list], columns=columns)], axis=0, ignore_index=True)
    return data


def click_next_button(wb):
    button = wb.find_element(by=By.CSS_SELECTOR, value='[aria-label=Next]').find_element(by=By.XPATH, value='..')
    # click if available
    if button.get_attribute('class') == 'page-item':
        button.click()
        return 0
    else:
        for i in range(10):
            if button.get_attribute('class') == 'page-item':
                button.click()
                return 0
            time.sleep(0.5)
    # if not stop script
    return 1


def click_next(wb):
    pages = wb.find_element(by=By.CLASS_NAME, value='pagination')
    #print(pages)


if __name__ == '__main__':
    print('Launching webdriver...')
    wb = run_webdriver()
    data = pd.DataFrame(columns=get_table_head(wb))
    page = 1

    select = Select(wb.find_element(by=By.TAG_NAME, value='select'))
    select.select_by_value('1: 25')

    while True:
        sys.stdout.write("\rPage %i" % page)
        sys.stdout.flush()
        page += 1
        data = get_data_from_page_html(wb, data)
        click_next(wb)
        if click_next_button(wb):
            break

    print()
    print(f'Collected {data.shape[0]} items.')
    print('Writing to the csv...')
    data.to_csv('table.csv', index=False)
    # stop webdriver
    wb.quit()
    print('Done!')