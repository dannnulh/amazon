# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-20 08:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('amazon', '0011_item_avg_unit_session_percentage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detailpagesalestraffic',
            name='sku',
        ),
    ]
