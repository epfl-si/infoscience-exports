# Generated by Django 2.0.2 on 2018-03-02 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exports', '0003_auto_20180223_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='export',
            name='groupsby_type',
            field=models.CharField(choices=[('NONE', ''), ('YEAR_TITLE', 'year: descending, year as title'), ('YEAR_PUBL', 'year: descending, with pending publications'), ('YEAR_TITLE_PUBL', 'year: descending, year as title, with pending publications'), ('DOC', 'document type'), ('DOC_TITLE', 'document type, document type as title')], default='NONE', max_length=255),
        ),
        migrations.AlterField(
            model_name='export',
            name='groupsby_year',
            field=models.CharField(choices=[('NONE', ''), ('YEAR_TITLE', 'year: descending, year as title'), ('YEAR_PUBL', 'year: descending, with pending publications'), ('YEAR_TITLE_PUBL', 'year: descending, year as title, with pending publications')], default='NONE', max_length=255),
        ),
    ]
