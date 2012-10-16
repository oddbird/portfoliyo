# -*- coding: utf-8 -*-
import datetime
import os
import time
from south.db import db
from south.v2 import DataMigration
from django.db import models


def get_default_school(orm):
    s, _ = orm.School.objects.get_or_create(
        name="Default School", postcode="00000")
    return s


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        default_school = get_default_school(orm)

        actual_schools = []
        for school_name in SCHOOLS:
            actual_schools.append(
                orm.School.objects.create(name=school_name, auto=False))

        for network in user_networks(orm):
            school_ids = set()
            for profileid in network:
                school_id = PROFILE_SCHOOLS.get(profileid)
                if school_id is not None:
                    school_ids.add(school_id)
            schools = [actual_schools[sid] for sid in school_ids]
            if len(schools) == 1:
                school = schools[0]
            elif not schools:
                school = orm.School.objects.create(
                    name=u"%f-%s" % (
                        time.time(),
                        "".join([str(pid) for pid in network]),
                        )[:200],
                    auto=True,
                    )
            else:
                raise ValueError("Too many schools (%s) in network %s" % (
                        ', '.join([s.name for s in schools]), network))

            orm.Profile.objects.filter(
                school=default_school, pk__in=network).update(
                school=school,
                )

        still_on_default = orm.Profile.objects.filter(school=default_school)
        if still_on_default.exists():
            raise ValueError(
                "Some profiles still have default school: %s" % (
                    ", ".join([p.id for p in still_on_default])))

        default_school.delete()


    def backwards(self, orm):
        "Write your backwards methods here."

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
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Profile']", 'null': 'True', 'blank': 'True'}),
            'invited_in_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Group']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.School']"}),
            'school_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'done'", 'max_length': '20'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'users.relationship': {
            'Meta': {'unique_together': "[('from_profile', 'to_profile', 'kind')]", 'object_name': 'Relationship'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'from_group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'relationships'", 'null': 'True', 'to': "orm['users.Group']"}),
            'from_profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'relationships_from'", 'to': "orm['users.Profile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'elder'", 'max_length': '20'}),
            'to_profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'relationships_to'", 'to': "orm['users.Profile']"})
        },
        'users.school': {
            'Meta': {'unique_together': "[('name', 'postcode')]", 'object_name': 'School'},
            'auto': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        }
    }

    complete_apps = ['users']
    symmetrical = True



def user_networks(orm):
    """
    Return list of sets of user IDs; each set is an isolated user network.

    """
    networks = []
    networks_by_user = {}

    for rel in orm.Relationship.objects.all():
        fpid, tpid = rel.from_profile_id, rel.to_profile_id

        fpid_net = networks_by_user.get(fpid)
        tpid_net = networks_by_user.get(tpid)
        if fpid_net and tpid_net:
            if fpid_net is tpid_net:
                continue
            fpid_net.update(tpid_net)
            for userid in tpid_net:
                networks_by_user[userid] = fpid_net
            networks.remove(tpid_net)
        elif fpid_net:
            fpid_net.add(tpid)
            networks_by_user[tpid] = fpid_net
        elif tpid_net:
            tpid_net.add(fpid)
            networks_by_user[fpid] = tpid_net
        else:
            net = {fpid, tpid}
            networks.append(net)
            networks_by_user[tpid] = net
            networks_by_user[fpid] = net

    # handle lone rangers
    for profile in orm.Profile.objects.exclude(pk__in=networks_by_user):
        net = {profile.id}
        networks_by_user[profile.id] = net
        networks.append(net)

    return networks


# proxy for "this is production"
if os.environ.get('AWS_STORAGE_BUCKET_NAME') == 'pyo-heroku':
    SCHOOLS = [
        'KIPP Philadelphia Charter School',
        'PFC Omar E. Torres Charter School',
        'KIPP West Philadelphia Charter School',
        'The Bronx School of Young Leaders',
        'Longfellow Middle School',
        'Francisco Modrano Middle School',
        'Saldivar Elementary School',
        'Thomas Jefferson High School',
        'KIPP Ascend Charter School',
        'Galapagos Charter School',
    ]

    PROFILE_SCHOOLS = {
        238: 2,
        244: 2,
        251: 9,
        39: 2,
        20: 3,
        45: 1,
        23: 1,
        28: 2,
        31: 0,
        5: 1,
        44: 1,
        245: 2,
        248: 8,
        250: 8,
        41: 2,
        139: 4,
        140: 4,
        143: 4,
        144: 4,
        145: 5,
        185: 6,
        160: 5,
        161: 5,
        162: 5,
        163: 5,
        164: 5,
        165: 5,
        166: 5,
        167: 5,
        168: 5,
        169: 5,
        170: 5,
        129: 0,
        177: 7,
        130: 0,
        134: 0,
        179: 7,
        211: 2,
        214: 2,
        246: 8,
        34: 0,
        35: 0,
        43: 2,
        236: 2,
        237: 2,
        63: 2,
        62: 2,
        64: 2,
        65: 2,
    }
else:
    SCHOOLS = []
    PROFILE_SCHOOLS = {}
