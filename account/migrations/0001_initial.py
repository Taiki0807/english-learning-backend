# Generated by Django 4.2.1 on 2023-05-14 07:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("username", models.CharField(max_length=255, unique=True, verbose_name="ユーザ名")),
                ("email", models.EmailField(max_length=255, null=True, verbose_name="Eメール")),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_admin", models.BooleanField(default=False)),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now)),
                ("login_date", models.DateTimeField(default=django.utils.timezone.now)),
                ("image", models.URLField(blank=True, max_length=1000, null=True, verbose_name="URL")),
            ],
            options={
                "db_table": "account",
            },
        ),
        migrations.CreateModel(
            name="OnlineUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
    ]