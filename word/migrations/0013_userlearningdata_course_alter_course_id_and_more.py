# Generated by Django 4.2.1 on 2023-06-04 10:31

from django.db import migrations, models
import django.db.models.deletion
import shortuuid.main


class Migration(migrations.Migration):
    dependencies = [
        ("word", "0012_remove_userlearningdata_course_alter_course_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userlearningdata",
            name="course",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="word.course"
            ),
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
