from copy import deepcopy

from django.contrib.auth.models import User as LegacyUser
from django.db import migrations


def repoint_clinic_user(apps, schema_editor):
    ClinicUser = apps.get_model('clinic', 'ClinicUser')
    new_field = ClinicUser._meta.get_field('user')
    old_field = deepcopy(new_field)
    old_field.remote_field.model = LegacyUser
    schema_editor.alter_field(ClinicUser, old_field, new_field, strict=False)


class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0003_repoint_admin_log_user'),
        ('clinic', '0003_doctor_experience_years_workschedule'),
    ]

    operations = [
        migrations.RunPython(repoint_clinic_user, migrations.RunPython.noop),
    ]
