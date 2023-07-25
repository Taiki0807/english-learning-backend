# Generated by Django 4.2.2 on 2023-07-02 08:56

from django.db import migrations, models
import shortuuid.main


class Migration(migrations.Migration):
    dependencies = [
        ("word", "0014_remove_userlearningdata_retention_rates_and_more"),
    ]

    operations = [
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
