from copy import deepcopy

from django.contrib.auth.models import User as LegacyUser
from django.db import migrations


def repoint_admin_log_user(apps, schema_editor):
    if 'django_admin_log' not in schema_editor.connection.introspection.table_names():
        return

    LogEntry = apps.get_model('admin', 'LogEntry')
    new_field = LogEntry._meta.get_field('user')
    old_field = deepcopy(new_field)
    old_field.remote_field.model = LegacyUser
    schema_editor.alter_field(LogEntry, old_field, new_field, strict=False)


class Migration(migrations.Migration):
    dependencies = [
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('authentication', '0002_copy_legacy_auth_users'),
    ]

    operations = [
        migrations.RunPython(repoint_admin_log_user, migrations.RunPython.noop),
    ]
