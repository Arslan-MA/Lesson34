# Generated by Django 4.2.7 on 2023-11-12 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_like_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='like',
            name='disliked',
            field=models.BooleanField(default=False),
        ),
    ]
