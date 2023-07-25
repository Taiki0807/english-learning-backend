# Generated by Django 4.2.1 on 2023-06-04 10:24

from django.db import migrations, models
import shortuuid.main


class Migration(migrations.Migration):
    dependencies = [
        ("word", "0011_remove_review_retention_rates_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userlearningdata",
            name="course",
        ),
        migrations.AlterField(
            model_name="course",
            name="id",
            field=models.CharField(
                default=shortuuid.main.ShortUUID.uuid, max_length=22, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="flashcard",
            name="id",
            field=models.CharField(
                default=shortuuid.main.ShortUUID.uuid, max_length=22, primary_key=True, serialize=False
            ),
        ),
    ]
