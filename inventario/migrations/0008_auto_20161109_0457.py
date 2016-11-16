# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-09 04:57
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20161104_2317'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventario', '0007_auto_20161107_0339'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_pedido', models.CharField(max_length=10)),
                ('stotal', models.FloatField()),
                ('impuesto', models.FloatField()),
                ('total', models.FloatField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('anulado', models.BooleanField(default=False)),
                ('fecha_anulacion', models.DateTimeField(null=True)),
                ('comentario', models.CharField(max_length=200, null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Cliente')),
                ('usuario_anulacion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pedido_usuario_anulacion', to=settings.AUTH_USER_MODEL)),
                ('usuario_creacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedido_usuario_creacion', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pedido_Detalle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.FloatField()),
                ('valor', models.FloatField()),
                ('bodega', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.Bodega')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.Pedido')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventario.Producto')),
            ],
        ),
        migrations.RemoveField(
            model_name='factura',
            name='cliente',
        ),
        migrations.AddField(
            model_name='factura',
            name='comentario',
            field=models.CharField(max_length=200, null=True),
        ),
    ]