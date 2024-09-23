import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, jsonify, Response
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
import os
from flask_migrate import Migrate
import logging

logging.basicConfig(level=logging.INFO)

# Flask app setup
app = Flask(__name__)

# Redis configuration
app.config['REDIS_URL'] = "redis://localhost:6379/0"
redis_client = FlaskRedis(app)

# PostgreSQL Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mma_user:password@localhost/mma_stats'
db = SQLAlchemy(app)

# Flask-Migrate setup
migrate = Migrate(app, db)

# Celery setup for background tasks
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Define the models for PostgreSQL
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    date = db.Column(db.String(100))
    link = db.Column(db.String(255))
    schedule_type = db.Column(db.String(20))
    fight_card = db.relationship('FightCard', backref='event', lazy=True)

class FightCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    fighterA = db.Column(db.String(100))
    fighterB = db.Column(db.String(100))
    weight = db.Column(db.String(50))
    result = db.Column(db.String(50), nullable=True)

BASE_URL = 'https://www.tapology.com'

# Celery task for scraping events
@celery.task
def scrape_events_async(schedule_type):
    with app.app_context():
        return scrape_events(schedule_type)

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
            fighterB_country = fighterB_el.select_one('img[class="opacity-70 h-[11px] w-[17px] border border-white md:border-0"]')

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
        date_element = event.select_one('.promotion span.hidden.md\\:inline')
        date = date_element.text.strip() if date_element else 'Unknown Date'
        link = title_element['href']
        event_url = f'{BASE_URL}{link}'

        # Check if the event exists in the database
        existing_event = Event.query.filter_by(link=event_url).first()
        if not existing_event:
            # Log event scraping
            logging.info(f"Scraping event: {title}")

            # Store the event and its fight card in the database
            new_event = Event(
                title=title,
                date=date,
                link=event_url,
                schedule_type=schedule_type  # Store whether it’s upcoming or past
            )
            db.session.add(new_event)
            db.session.commit()

            if schedule_type == 'upcoming':
                fight_card = scrape_fight_card(event_url)
            else:
                fight_card = scrape_fight_card_results(event_url)

            for fight in fight_card:
                logging.info(f"Scraping fight: {fight['fighterA']['name']} vs {fight['fighterB']['name']}")
                new_fight = FightCard(
                    event_id=new_event.id,
                    fighterA=fight['fighterA']['name'],
                    fighterB=fight['fighterB']['name'],
                    weight=fight['weight'],
                    result=fight['fighterA'].get('result', 'N/A') if 'result' in fight['fighterA'] else None  # Save result
                )
                db.session.add(new_fight)

            db.session.commit()

        events.append({
            'title': title,
            'date': date,
            'link': event_url
        })

    # Update Redis cache after scraping
    cache_key = 'upcoming_events' if schedule_type == 'upcoming' else 'past_results'
    redis_client.set(cache_key, json.dumps(events), ex=3600)  # Cache for 1 hour

    return events

@app.route('/upcoming', methods=['GET'])
def get_upcoming():
    cached = redis_client.get('upcoming_events')
    if cached:
        return Response(cached, mimetype='application/json')

    try:
        # Fetch only upcoming events from the database
        events = Event.query.filter_by(schedule_type='upcoming').all()
        response_data = [{
            'title': event.title,
            'date': event.date,
            'link': event.link,
            'fight_card': [
                {
                    'fighterA': fight.fighterA,
                    'fighterB': fight.fighterB,
                    'weight': fight.weight,
                    'result': fight.result
                } for fight in event.fight_card
            ]
        } for event in events]

        response_json = json.dumps(response_data, ensure_ascii=False)

        # Cache the result in Redis for 1 hour
        redis_client.set('upcoming_events', response_json, ex=3600)

        return Response(response_json, mimetype='application/json')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results', methods=['GET'])
def get_results():
    cached = redis_client.get('past_results')
    if cached:
        return Response(cached, mimetype='application/json')

    try:
        # Fetch only past events from the database
        events = Event.query.filter_by(schedule_type='results').all()
        response_data = [{
            'title': event.title,
            'date': event.date,
            'link': event.link,
            'fight_card': [
                {
                    'fighterA': fight.fighterA,
                    'fighterB': fight.fighterB,
                    'weight': fight.weight,
                    'result': fight.result
                } for fight in event.fight_card
            ]
        } for event in events]

        response_json = json.dumps(response_data, ensure_ascii=False)

        # Cache the result in Redis for 1 hour
        redis_client.set('past_results', response_json, ex=3600)

        return Response(response_json, mimetype='application/json')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trigger_scrape_upcoming', methods=['POST'])
def trigger_scrape_upcoming():
    scrape_events_async.delay('upcoming')
    redis_client.delete('upcoming_events') 
    return jsonify({'status': 'Scraping upcoming events in background'})

@app.route('/trigger_scrape_results', methods=['POST'])
def trigger_scrape_results():
    scrape_events_async.delay('results')
    redis_client.delete('past_results') 
    return jsonify({'status': 'Scraping results in background'})
if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)