# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-04 20:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_gestion_descripcion'),
    ]

    operations = [
        migrations.AddField(
            model_name='gestion',
            name='programacion',
            field=models.DateField(blank=True, null=True),
        ),
    ]
