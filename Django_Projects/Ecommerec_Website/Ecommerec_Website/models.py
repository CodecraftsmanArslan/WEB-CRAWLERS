from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    confirm_password = models.CharField(max_length=100)

    def __str__(self):
        return self.username
    


class Product(models.Model):
    title = models.CharField(max_length=100)
    header_image=models.ImageField(null=True,blank=True,upload_to="images/")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title

