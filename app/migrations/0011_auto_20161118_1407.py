# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-18 14:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20161116_2144'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Factura_Abono',
            new_name='Documento_Abono',
        ),
        migrations.RenameModel(
            old_name='Factura',
            new_name='Documento_Cobro',
        ),
    ]