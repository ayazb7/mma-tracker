import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

BASE_URL = 'https://www.tapology.com'

async def fetch_page_content(event_url):
    """
    Fetches the page content using Playwright.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(event_url)
        content = await page.content()
        await browser.close()
    return content

async def scrape_fight_card(event_url):
    """
    Asynchronously scrapes the fight card for a given event using Playwright.
    """
    content = await fetch_page_content(event_url)
    soup = BeautifulSoup(content, 'html.parser')
    fight_card = []

    fights_list = soup.select('#sectionFightCard ul.mt-5 li[data-controller="table-row-background"]')
    
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

    return fight_card

async def scrape_fight_card_results(event_url):
    """
    Asynchronously scrapes fight results using Playwright.
    """
    content = await fetch_page_content(event_url)
    soup = BeautifulSoup(content, 'html.parser')
    fight_card = []

    fights_list = soup.select('#sectionFightCard ul.mt-5 li[data-controller="table-row-background"]')
    
    for fight in fights_list:
        weight_el = fight.select_one('span[class="bg-tap_darkgold px-1.5 md:px-1 leading-[23px] text-sm md:text-[13px] text-neutral-50 rounded"]')
        fighterA_el = fight.select_one('div[class="div flex flex-col justify-around md:justify-center rounded w-full md:pr-[5px] h-[77px] md:h-[77px] bg-gradient-to-r from-[#d1f7d2] to-[#e3fce3] items-center md:items-end"]')
        fighterB_el = fight.select_one('div[class="div flex flex-col justify-around md:justify-center rounded w-full md:pl-[5px] h-[77px] md:h-[77px] bg-gradient-to-r from-[#ffecec] to-[#efd7d7] items-center md:items-start"]')
        
        countryA_el = fighterA_el.select_one('div[class="div flex flex-col md:flex-row text-xs11 text-tap_3 md:h-[26px] leading-none items-center gap-2.5 md:gap-1"]')
        countryB_el = fighterB_el.select_one('div[class="div flex flex-col md:flex-row text-xs11 text-tap_3 md:h-[26px] leading-none items-center gap-2.5 md:gap-1"]')
        
        recordA_el = fighterA_el.select_one('div[class="div flex flex-col md:flex-row md:h-[26px] leading-none items-center gap-1"]')
        recordB_el = fighterB_el.select_one('div[class="div flex flex-col md:flex-row md:h-[26px] leading-none items-center gap-1"]')
        
        # Extract the fighter result for fighter A and fighter B
        fighterA_result_el = fighterA_el.select_one('span[class^="text-"]')
        fighterB_result_el = fighterB_el.select_one('span[class^="text-"]')
        
        result_mapping = {
            "text-neutral-100": "NC",
            "text-green-100": "Win",
            "text-red-100": "Loss",
            "text-blue-100": "Draw"
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

    return fight_card