# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Profile'
        db.create_table('users_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=255)),
            ('receive_emails', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('birthdate', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('pic', self.gf('django.db.models.fields.files.ImageField')(max_length=255, blank=True)),
            ('altpic', self.gf('django.db.models.fields.files.ImageField')(max_length=255, blank=True)),
            ('fave_subject', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('fave_food', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('fave_sport', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('fave_color', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('users', ['Profile'])

        # Adding model 'Relationship'
        db.create_table('users_relationship', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='relationships_from', to=orm['auth.User'])),
            ('to_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='relationships_to', to=orm['auth.User'])),
            ('relationship', self.gf('django.db.models.fields.CharField')(default='supports', max_length=20)),
            ('notifications', self.gf('django.db.models.fields.CharField')(default='email', max_length=20)),
        ))
        db.send_create_signal('users', ['Relationship'])


    def backwards(self, orm):
        # Deleting model 'Profile'
        db.delete_table('users_profile')

        # Deleting model 'Relationship'
        db.delete_table('users_relationship')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'users.profile': {
            'Meta': {'object_name': 'Profile'},
            'altpic': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'blank': 'True'}),
            'birthdate': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'fave_color': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'fave_food': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'fave_sport': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'fave_subject': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pic': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'blank': 'True'}),
            'receive_emails': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'users.relationship': {
            'Meta': {'object_name': 'Relationship'},
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'relationships_from'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notifications': ('django.db.models.fields.CharField', [], {'default': "'email'", 'max_length': '20'}),
            'relationship': ('django.db.models.fields.CharField', [], {'default': "'supports'", 'max_length': '20'}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'relationships_to'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['users']