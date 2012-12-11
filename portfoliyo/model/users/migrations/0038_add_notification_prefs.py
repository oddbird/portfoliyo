# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Profile.notify_new_parent'
        db.add_column('users_profile', 'notify_new_parent',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Profile.notify_parent_text'
        db.add_column('users_profile', 'notify_parent_text',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Profile.notify_added_to_village'
        db.add_column('users_profile', 'notify_added_to_village',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Profile.notify_joined_my_village'
        db.add_column('users_profile', 'notify_joined_my_village',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Profile.notify_teacher_post'
        db.add_column('users_profile', 'notify_teacher_post',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Profile.notify_new_parent'
        db.delete_column('users_profile', 'notify_new_parent')

        # Deleting field 'Profile.notify_parent_text'
        db.delete_column('users_profile', 'notify_parent_text')

        # Deleting field 'Profile.notify_added_to_village'
        db.delete_column('users_profile', 'notify_added_to_village')

        # Deleting field 'Profile.notify_joined_my_village'
        db.delete_column('users_profile', 'notify_joined_my_village')

        # Deleting field 'Profile.notify_teacher_post'
        db.delete_column('users_profile', 'notify_teacher_post')


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
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
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
        'users.group': {
            'Meta': {'object_name': 'Group'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'elders': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'elder_in_groups'", 'blank': 'True', 'to': "orm['users.Profile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_groups'", 'to': "orm['users.Profile']"}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'student_in_groups'", 'blank': 'True', 'to': "orm['users.Profile']"})
        },
        'users.profile': {
            'Meta': {'object_name': 'Profile'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'declined': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email_notifications': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Profile']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'notify_added_to_village': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'notify_joined_my_village': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'notify_new_parent': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'notify_parent_text': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'notify_teacher_post': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.School']"}),
            'school_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'users.relationship': {
            'Meta': {'unique_together': "[('from_profile', 'to_profile', 'kind')]", 'object_name': 'Relationship'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'direct': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'from_profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'relationships_from'", 'to': "orm['users.Profile']"}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'relationships'", 'blank': 'True', 'to': "orm['users.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'elder'", 'max_length': '20'}),
            'level': ('django.db.models.fields.CharField', [], {'default': "'normal'", 'max_length': '20'}),
            'to_profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'relationships_to'", 'to': "orm['users.Profile']"})
        },
        'users.school': {
            'Meta': {'unique_together': "[('name', 'postcode')]", 'object_name': 'School'},
            'auto': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'users.textsignup': {
            'Meta': {'object_name': 'TextSignup'},
            'family': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'signups'", 'to': "orm['users.Profile']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'kidname'", 'max_length': '20'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'family_signups'", 'null': 'True', 'to': "orm['users.Profile']"}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'signed_up'", 'to': "orm['users.Profile']"})
        }
    }

    complete_apps = ['users']