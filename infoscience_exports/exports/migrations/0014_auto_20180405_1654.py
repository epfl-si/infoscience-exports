# Generated by Django 2.0.3 on 2018-04-05 14:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exports', '0013_legacyexport'),
    ]

    operations = [
        migrations.RenameField(
            model_name='legacyexport',
            old_name='place',
            new_name='export',
        ),
    ]
