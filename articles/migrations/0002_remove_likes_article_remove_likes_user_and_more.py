# Generated by Django 4.1.7 on 2023-03-01 09:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='likes',
            name='article',
        ),
        migrations.RemoveField(
            model_name='likes',
            name='user',
        ),
        migrations.DeleteModel(
            name='Comments',
        ),
        migrations.DeleteModel(
            name='Likes',
        ),
    ]
