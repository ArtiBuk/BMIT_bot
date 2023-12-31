# Generated by Django 4.2.2 on 2023-06-14 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Projects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='Название проекта')),
                ('short_description', models.CharField(blank=True, max_length=64, verbose_name='Краткое описание')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='projects',
            field=models.ManyToManyField(blank=True, related_name='users', to='back.projects'),
        ),
    ]
