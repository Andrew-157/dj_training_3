# Generated by Django 4.1.7 on 2023-03-05 09:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0005_like_dislike'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='like',
            name='article',
        ),
        migrations.RemoveField(
            model_name='like',
            name='author',
        ),
        migrations.DeleteModel(
            name='Dislike',
        ),
        migrations.DeleteModel(
            name='Like',
        ),
    ]
