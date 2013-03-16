# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Post', fields ['url']
        db.delete_unique(u'feeds_post', ['url'])

        # Adding field 'Post.url_hash'
        db.add_column(u'feeds_post', 'url_hash',
                      self.gf('django.db.models.fields.CharField')(default='', unique=True, max_length=64),
                      keep_default=False)


        # Changing field 'Post.url'
        db.alter_column(u'feeds_post', 'url', self.gf('django.db.models.fields.URLField')(max_length=4096))

    def backwards(self, orm):
        # Deleting field 'Post.url_hash'
        db.delete_column(u'feeds_post', 'url_hash')


        # Changing field 'Post.url'
        db.alter_column(u'feeds_post', 'url', self.gf('django.db.models.fields.URLField')(max_length=256, unique=True))
        # Adding unique constraint on 'Post', fields ['url']
        db.create_unique(u'feeds_post', ['url'])


    models = {
        u'feeds.post': {
            'Meta': {'ordering': "('-created_at',)", 'object_name': 'Post'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'captured_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posts'", 'to': u"orm['feeds.Site']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
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