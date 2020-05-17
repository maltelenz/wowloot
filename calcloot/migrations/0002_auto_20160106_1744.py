# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-06 16:44
from __future__ import unicode_literals

from django.db import migrations

def set_default_values(apps, schema_editor):
    Currency = apps.get_model("calcloot", "Currency")
    Currency.objects.get_or_create(name='USD', rate=1.0)


class Migration(migrations.Migration):

    dependencies = [
        ('calcloot', '0001_initial'),
    ]

    operations = [
    	migrations.RunPython(set_default_values),
    ]