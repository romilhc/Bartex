# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-08 23:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarterSystem', '0002_auto_20170417_0149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='swap',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]