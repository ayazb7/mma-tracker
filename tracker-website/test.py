import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, jsonify, Response
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


BASE_URL = 'https://www.tapology.com'

def scrape_fight_card(event_url):
    """
    Scrapes the fight card for a given event using Selenium to handle dynamic content.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(event_url)
        
        time.sleep(0.5)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        fight_card = []

        fights_list = soup.select('#sectionFightCard ul.mt-5 li[data-controller="table-row-background"]')
        
        print(f"{event_url} length: {len(fights_list)}")

        for fight in fights_list:
            weight_el = fight.select_one('span[class="bg-tap_darkgold px-1.5 md:px-1 leading-[23px] text-sm md:text-[13px] text-neutral-50 rounded"]')
            fighterA_el = fight.select_one('div[class="div flex flex-col justify-around md:justify-center rounded w-full md:pr-[5px] h-[77px] md:h-[77px] bg-gradient-to-r from-[ffffff] to-[#ffffff] items-center md:items-end"]')
            fighterB_el = fight.select_one('div[class="div flex flex-col justify-around md:justify-center rounded w-full md:pl-[5px] h-[77px] md:h-[77px] bg-gradient-to-r from-[#ffffff] to-[ffffff] items-center md:items-start"]')
            
            infoA_el = fighterA_el.select_one('div[class="div flex flex-col md:flex-row text-xs11 text-tap_3 md:h-[26px] leading-none items-center gap-2.5 md:gap-1"]')
            infoB_el = fighterB_el.select_one('div[class="div flex flex-col md:flex-row text-xs11 text-tap_3 md:h-[26px] leading-none items-center gap-2.5 md:gap-1"]')
            
            fight_card.append({
                'fighterA': {
                    "name": fighterA_el.select_one('a[class="link-primary-red"]').text.strip(),
                    "record": infoA_el.select_one('span[class="text-[15px] md:text-xs order-2"]').text.strip(),
                    "country": infoA_el.select_one('img[class="opacity-70 h-[14px] md:h-[11px] w-[22px] md:w-[17px]"]')['src']
                },
                'fighterB': {
                    "name": fighterB_el.select_one('a[class="link-primary-red"]').text.strip(),
                    "record": infoB_el.select_one('span[class="text-[15px] md:text-xs order-1"]').text.strip(),
                    "country": infoB_el.select_one('img[class="opacity-70 h-[14px] md:h-[11px] w-[22px] md:w-[17px]"]')['src']
                },
                'weight': weight_el.text.strip()
            })

    finally:
        driver.quit()

    return fight_card

def scrape_fight_card_results(event_url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(event_url)
        
        time.sleep(0.5)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        fight_card = []

        fights_list = soup.select('#sectionFightCard ul.mt-5 li[data-controller="table-row-background"]')
        
        print(f"{event_url} length: {len(fights_list)}")

        for fight in fights_list:
            weight_el = fight.select_one('span[class="bg-tap_darkgold px-1.5 md:px-1 leading-[23px] text-sm md:text-[13px] text-neutral-50 rounded"]')
            fighterA_el = fight.select_one('div[class="div flex flex-col justify-around md:justify-center rounded w-full md:pr-[5px] h-[77px] md:h-[77px] bg-gradient-to-r from-[#d1f7d2] to-[#e3fce3] items-center md:items-end"]')
            fighterB_el = fight.select_one('div[class="div flex flex-col justify-around md:justify-center rounded w-full md:pl-[5px] h-[77px] md:h-[77px] bg-gradient-to-r from-[#ffecec] to-[#efd7d7] items-center md:items-start"]')
            
            countryA_el = fighterA_el.select_one('div[class="div flex flex-col md:flex-row text-xs11 text-tap_3 md:h-[26px] leading-none items-center gap-2.5 md:gap-1"]')
            countryB_el = fighterB_el.select_one('div[class="div flex flex-col md:flex-row text-xs11 text-tap_3 md:h-[26px] leading-none items-center gap-2.5 md:gap-1"]')
            
            recordA_el = fighterA_el.select_one('div[class="div flex flex-col md:flex-row md:h-[26px] leading-none items-center gap-1"]')
            recordB_el = fighterB_el.select_one('div[class="div flex flex-col md:flex-row md:h-[26px] leading-none items-center gap-1"]')
            
            # Extract the fighter result for fighter A and fighter B
            fighterA_result_el = fighterA_el.select_one('span[class^="text-"]')  # Class starts with "text-"
            fighterB_result_el = fighterB_el.select_one('span[class^="text-"]')  # Class starts with "text-"
            
            # Map the result to the corresponding value
            result_mapping = {
                "text-neutral-100": "NC",   # No Contest (N)
                "text-green-100": "Win",    # Win (W)
                "text-red-100": "Loss",     # Loss (L)
                "text-blue-100": "Draw"     # Draw (D)
            }
            
            fighterA_result = result_mapping.get(fighterA_result_el['class'][0], "Unknown") if fighterA_result_el else 'Unknown'
            fighterB_result = result_mapping.get(fighterB_result_el['class'][0], "Unknown") if fighterB_result_el else 'Unknown'
            
            fighterA_record = recordA_el.select_one('span[class="text-[15px] md:text-xs leading-tight text-green-900"]')
            fighterB_record = recordB_el.select_one('span[class="text-[15px] md:text-xs leading-tight text-red-900"]')

            fighterA_country = countryA_el.select_one('img[class="opacity-70 h-[11px] w-[17px] border border-white md:border-0"]')
            fighterB_country = countryB_el.select_one('img[class="opacity-70 h-[11px] w-[17px] border border-white md:border-0"]')
            
            fight_card.append({
                'fighterA': {
                    "name": fighterA_el.select_one('a[class="link-primary-red"]').text.strip(),
                    "record": fighterA_record.text.strip() if fighterA_record else 'N/A',
                    "country": fighterA_country['src'] if fighterA_country else 'N/A',
                    "result": fighterA_result
                },
                'fighterB': {
                    "name": fighterB_el.select_one('a[class="link-primary-red"]').text.strip(),
                    "record": fighterB_record.text.strip() if fighterB_record else 'N/A',
                    "country": fighterB_country['src'] if fighterB_country else 'N/A',
                    "result": fighterB_result
                },
                'weight': weight_el.text.strip() if weight_el else 'N/A'
            })

    finally:
        driver.quit()

    return fight_card


def scrape_events(schedule_type):
    url = f'{BASE_URL}/fightcenter?group=ufc&schedule={schedule_type}'
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from Tapology for {schedule_type}")

    soup = BeautifulSoup(response.text, 'html.parser')

    events = []
    
    for event in soup.select('.fightcenterEvents > div.flex')[:5]:
        title_element = event.select_one('.promotion a')
        if not title_element:
            continue
        
        title = title_element.text.strip()

        if 'UFC' not in title:
            continue
        
        date_element = event.select_one('.promotion span.hidden.md\\:inline')
        date = date_element.text.strip() if date_element else 'Unknown Date'

        link = title_element['href']
        event_url = f'https://www.tapology.com{link}'

        if schedule_type == 'upcoming':
            fight_card = scrape_fight_card(event_url)
        else: 
            fight_card = scrape_fight_card_results(event_url)

        events.append({
            'title': title,
            'date': date,
            'link': event_url,
            'fight_card': fight_card 
        })

    return events

def scrape_upcoming_events():
    return scrape_events('upcoming')

def scrape_past_results():
    return scrape_events('results')

app = Flask(__name__)

@app.route('/upcoming', methods=['GET'])
def get_upcoming():
    try:
        events = scrape_upcoming_events()
        return Response(json.dumps(events, ensure_ascii=False), mimetype='application/json')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results', methods=['GET'])
def get_results():
    try:
        results = scrape_past_results()
        return Response(json.dumps(results, ensure_ascii=False), mimetype='application/json')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
