# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-26 18:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20161215_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='empresa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Empresa'),
        ),
    ]