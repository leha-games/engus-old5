# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0009_auto_20150212_1518'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='cards',
        ),
    ]
