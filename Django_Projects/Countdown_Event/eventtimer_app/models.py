from django.db import models

class Event(models.Model):
    event = models.IntegerField()


    def __str__(self):
        return str(self.event)  # Return a string representation of the object