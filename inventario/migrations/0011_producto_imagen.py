# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-11 05:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0010_pedido_vendedor'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='imagen',
            field=models.ImageField(null=True, upload_to=b''),
        ),
    ]