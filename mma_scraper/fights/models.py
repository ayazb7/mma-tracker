from django.db import models

class Fighter(models.Model):
    name = models.CharField(max_length=100)
    record = models.CharField(max_length=20) 
    country = models.URLField()
    result = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name

class Fight(models.Model):
    fighterA = models.ForeignKey(Fighter, related_name='fighterA_fights', on_delete=models.CASCADE)
    fighterB = models.ForeignKey(Fighter, related_name='fighterB_fights', on_delete=models.CASCADE)
    weight = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.fighterA.name} vs {self.fighterB.name}"

class Event(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    date = models.CharField(max_length=100)  # Store the date as a string; you could also use DateTimeField.

    fights = models.ManyToManyField(Fight)  # An event can have multiple fights.

    def __str__(self):
        return self.title