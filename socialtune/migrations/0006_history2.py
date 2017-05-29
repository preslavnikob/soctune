# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-01-17 00:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('socialtune', '0005_auto_20170117_0050'),
    ]

    operations = [
        migrations.CreateModel(
            name='History2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_field', models.IntegerField()),
                ('product', models.CharField(default='', max_length=200)),
                ('action', models.CharField(default='', max_length=200)),
                ('text', models.CharField(default='', max_length=200)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socialtune.Users')),
            ],
        ),
    ]