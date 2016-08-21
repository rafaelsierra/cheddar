# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('feeds', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=32)),
                ('user', models.ForeignKey(related_name='folders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='UserPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_read', models.BooleanField(default=False, db_index=True)),
                ('is_starred', models.BooleanField(default=False, db_index=True)),
                ('is_shared', models.BooleanField(default=False, db_index=True)),
                ('post', models.ForeignKey(related_name='userpost', to='feeds.Post')),
                ('user', models.ForeignKey(related_name='my_posts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('folder', models.ForeignKey(related_name='usersite', blank=True, to='accounts.Folder', null=True)),
                ('site', models.ForeignKey(related_name='usersite', to='feeds.Site')),
                ('user', models.ForeignKey(related_name='my_sites', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='usersite',
            unique_together=set([('user', 'site')]),
        ),
        migrations.AlterUniqueTogether(
            name='userpost',
            unique_together=set([('user', 'post')]),
        ),
    ]
