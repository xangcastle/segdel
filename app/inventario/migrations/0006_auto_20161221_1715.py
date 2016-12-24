# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-21 23:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0005_auto_20161215_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='categoria',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventario.Producto_Categoria'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='marca',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventario.Producto_Marca'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='medida',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventario.Producto_Medida'),
        ),
    ]