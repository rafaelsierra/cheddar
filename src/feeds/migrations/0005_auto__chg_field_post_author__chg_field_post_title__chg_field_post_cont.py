# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Post.author'
        db.alter_column(u'feeds_post', 'author', self.gf('django.db.models.fields.CharField')(max_length=64, null=True))

        # Changing field 'Post.title'
        db.alter_column(u'feeds_post', 'title', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True))

        # Changing field 'Post.content'
        db.alter_column(u'feeds_post', 'content', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # Changing field 'Post.author'
        db.alter_column(u'feeds_post', 'author', self.gf('django.db.models.fields.CharField')(default='', max_length=64))

        # Changing field 'Post.title'
        db.alter_column(u'feeds_post', 'title', self.gf('django.db.models.fields.CharField')(default='', max_length=1024))

        # Changing field 'Post.content'
        db.alter_column(u'feeds_post', 'content', self.gf('django.db.models.fields.TextField')(default=''))

    models = {
        u'feeds.post': {
            'Meta': {'ordering': "('-created_at',)", 'object_name': 'Post'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'captured_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posts'", 'to': u"orm['feeds.Site']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '4096'}),
            'url_hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        u'feeds.site': {
            'Meta': {'object_name': 'Site'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'feed_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['feeds']