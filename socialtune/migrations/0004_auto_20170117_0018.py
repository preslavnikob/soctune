# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-01-17 00:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialtune', '0003_history2'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='followed_by',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='users',
            name='follows',
            field=models.IntegerField(default=0),
        ),
    ]
