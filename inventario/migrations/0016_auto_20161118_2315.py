# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-18 23:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0015_auto_20161118_2315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recibo_provicional',
            name='comentario',
            field=models.CharField(max_length=600, null=True),
        ),
    ]
