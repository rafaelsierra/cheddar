# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=1024, null=True, blank=True)),
                ('content', models.TextField(null=True, blank=True)),
                ('author', models.CharField(max_length=64, null=True, blank=True)),
                ('url', models.URLField(max_length=4096)),
                ('url_hash', models.CharField(unique=True, max_length=64)),
                ('captured_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('url', models.URLField(null=True, blank=True)),
                ('feed_url', models.URLField(unique=True)),
                ('title', models.CharField(max_length=256, null=True, blank=True)),
                ('feed_errors', models.IntegerField(default=0)),
                ('last_update', models.DateTimeField()),
                ('next_update', models.DateTimeField(db_index=True)),
                ('task_id', models.CharField(default=b'', max_length=36, null=True, blank=True)),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.AlterIndexTogether(
            name='site',
            index_together=set([('feed_errors', 'last_update')]),
        ),
        migrations.AddField(
            model_name='post',
            name='site',
            field=models.ForeignKey(related_name='posts', to='feeds.Site'),
        ),
    ]
