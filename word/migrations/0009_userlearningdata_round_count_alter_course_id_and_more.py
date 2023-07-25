# Generated by Django 4.2.1 on 2023-06-04 05:15

from django.db import migrations, models
import shortuuid.main


class Migration(migrations.Migration):
    dependencies = [
        ("word", "0008_retentionrate_alter_course_id_alter_flashcard_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userlearningdata",
            name="round_count",
            field=models.PositiveIntegerField(default=0),
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
