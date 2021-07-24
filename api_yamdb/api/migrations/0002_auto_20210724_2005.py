# Generated by Django 2.2.6 on 2021-07-24 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='title',
            index=models.Index(fields=['category'], name='api_title_categor_5e604c_idx'),
        ),
        migrations.AddIndex(
            model_name='title',
            index=models.Index(fields=['name'], name='api_title_name_350714_idx'),
        ),
        migrations.AddIndex(
            model_name='title',
            index=models.Index(fields=['year'], name='api_title_year_10c411_idx'),
        ),
    ]