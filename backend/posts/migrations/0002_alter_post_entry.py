# Generated by Django 4.1.4 on 2022-12-18 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='entry',
            field=models.TextField(blank=True, null=True),
        ),
    ]