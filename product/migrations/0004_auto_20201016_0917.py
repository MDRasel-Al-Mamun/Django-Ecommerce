# Generated by Django 3.1.1 on 2020-10-16 03:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-id']},
        ),
    ]