# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = [('users', '0001_initial')]

    def forwards(self, orm):
        # Adding model 'Announcement'
        db.create_table('announce_announcement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('announce', ['Announcement'])


    def backwards(self, orm):
        # Deleting model 'Announcement'
        db.delete_table('announce_announcement')


    models = {
        'announce.announcement': {
            'Meta': {'object_name': 'Announcement'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }

    complete_apps = ['announce']
