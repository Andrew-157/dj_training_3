# Generated by Django 4.1.7 on 2023-03-09 07:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0013_article_tags'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='articlereading',
            options={'ordering': ['-times_read']},
        ),
    ]
