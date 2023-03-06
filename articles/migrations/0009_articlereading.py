# Generated by Django 4.1.7 on 2023-03-06 07:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0008_reaction_remove_like_article_remove_like_author_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleReading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('times_read', models.PositiveBigIntegerField(default=0)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.article')),
            ],
        ),
    ]
