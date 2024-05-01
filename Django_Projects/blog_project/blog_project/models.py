from django.db import models

class YourModelName(models.Model):
    title = models.CharField(max_length=255, null=False)
    header_image=models.ImageField(null=True,blank=True,upload_to="images/")
    description = models.TextField()

    def __str__(self):
        return self.title
