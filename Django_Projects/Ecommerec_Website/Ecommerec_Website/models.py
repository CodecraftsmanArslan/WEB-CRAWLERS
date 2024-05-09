from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db import models
from PIL import Image



def validate_image_size(image):
    img = Image.open(image)
    if img.width != 800 or img.height != 800:
        raise ValidationError("Image must be 800x800 pixels.")

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    confirm_password = models.CharField(max_length=100)

    def __str__(self):
        return self.username
    
class Product(models.Model):
    title = models.CharField(max_length=100)
    header_image = models.ImageField(null=True, blank=True, upload_to="images/", validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']), validate_image_size])
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title
    

class CardItem(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title


