from rest_framework.decorators import api_view
from rest_framework.response import Response
from .scraping.scraper import scrape_fight_card, scrape_fight_card_results
from .models import Fighter, Fight, Event
from .serializers import EventSerializer

@api_view(['GET'])
async def get_upcoming_fights(request):
    event_url = 'https://www.tapology.com/fightcenter/upcoming'
    event_data = await scrape_fight_card(event_url)
    
    # Create or update Event
    event, _ = Event.objects.update_or_create(
        title=event_data['title'],
        defaults={
            'link': event_data['link'],
            'date': event_data['date']
        }
    )

    for fight in event_data['fight_card']:
        fighterA_data = fight['fighterA']
        fighterB_data = fight['fighterB']

        # Create or update FighterA
        fighterA, _ = Fighter.objects.update_or_create(
            name=fighterA_data['name'],
            defaults={
                'record': fighterA_data['record'],
                'country': fighterA_data['country'],
            }
        )

        # Create or update FighterB
        fighterB, _ = Fighter.objects.update_or_create(
            name=fighterB_data['name'],
            defaults={
                'record': fighterB_data['record'],
                'country': fighterB_data['country'],
            }
        )

        # Create or update Fight
        fight_instance, _ = Fight.objects.update_or_create(
            fighterA=fighterA,
            fighterB=fighterB,
            defaults={'weight': fight['weight']}
        )

        # Associate the fight with the event
        event.fights.add(fight_instance)

    # Serialize the event to return it as a response
    serializer = EventSerializer(event)
    return Response(serializer.data)

@api_view(['GET'])
async def get_fight_results(request):
    event_url = 'https://www.tapology.com/fightcenter/results'  # Example
    event_data = await scrape_fight_card_results(event_url)

    # Create or update Event
    event, _ = Event.objects.update_or_create(
        title=event_data['title'],
        defaults={
            'link': event_data['link'],
            'date': event_data['date']
        }
    )

    for fight in event_data['fight_card']:
        fighterA_data = fight['fighterA']
        fighterB_data = fight['fighterB']

        # Create or update FighterA
        fighterA, _ = Fighter.objects.update_or_create(
            name=fighterA_data['name'],
            defaults={
                'record': fighterA_data['record'],
                'country': fighterA_data['country'],
            }
        )

        # Create or update FighterB
        fighterB, _ = Fighter.objects.update_or_create(
            name=fighterB_data['name'],
            defaults={
                'record': fighterB_data['record'],
                'country': fighterB_data['country'],
            }
        )

        # Create or update Fight
        fight_instance, _ = Fight.objects.update_or_create(
            fighterA=fighterA,
            fighterB=fighterB,
            defaults={'weight': fight['weight']}
        )

        # Associate the fight with the event
        event.fights.add(fight_instance)

    # Serialize the event to return it as a response
    serializer = EventSerializer(event)
    return Response(serializer.data)