from django.urls import path
from .views import get_upcoming_fights, get_fight_results

urlpatterns = [
    path('upcoming/', get_upcoming_fights, name='get_upcoming_fights'),
    path('results/', get_fight_results, name='get_fight_results'),
]