# Generated by Django 4.2.2 on 2023-06-15 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0007_alter_report_hours'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='text_report',
            field=models.TextField(default=1, verbose_name='Отчет'),
            preserve_default=False,
        ),
    ]
