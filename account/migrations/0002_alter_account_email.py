# Generated by Django 4.2.1 on 2023-05-25 15:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="account",
            name="email",
            field=models.EmailField(max_length=255, null=True, unique=True, verbose_name="Eメール"),
        ),
    ]
