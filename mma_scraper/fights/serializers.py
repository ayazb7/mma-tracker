from rest_framework import serializers
from .models import Fighter, Fight, Event

class FighterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fighter
        fields = '__all__'

class FightSerializer(serializers.ModelSerializer):
    fighterA = FighterSerializer()
    fighterB = FighterSerializer()

    class Meta:
        model = Fight
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    fights = FightSerializer(many=True)

    class Meta:
        model = Event
        fields = '__all__'