from django.db import models

class Video(models.Model):
    link = models.URLField(max_length=200)  # Adjust max_length as needed
    
    
    def __str__(self):
        return self.link  