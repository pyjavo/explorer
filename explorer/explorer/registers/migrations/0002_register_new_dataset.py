# Generated by Django 3.2.9 on 2021-12-02 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='register',
            name='new_dataset',
            field=models.JSONField(default=dict),
        ),
    ]
