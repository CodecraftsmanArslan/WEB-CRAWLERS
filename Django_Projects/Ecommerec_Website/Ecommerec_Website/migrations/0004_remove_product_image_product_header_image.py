# Generated by Django 5.0.4 on 2024-05-01 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerec_Website', '0003_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
        migrations.AddField(
            model_name='product',
            name='header_image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
