# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-18 17:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TczHour',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tcz_date', models.DateField(verbose_name='Datum')),
                ('tcz_user_change', models.CharField(default='Frei', max_length=20)),
                ('tcz_court', models.IntegerField()),
                ('tcz_hour', models.IntegerField(default=0)),
                ('tcz_free', models.BooleanField(default=False)),
                ('tcz_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]