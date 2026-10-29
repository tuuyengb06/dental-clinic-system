from django.core.management.color import no_style
from django.db import migrations
from django.utils import timezone


def copy_legacy_users(apps, schema_editor):
    connection = schema_editor.connection
    alias = connection.alias
    table_names = set(connection.introspection.table_names())
    if 'auth_user' not in table_names:
        return

    User = apps.get_model('authentication', 'User')
    with connection.cursor() as cursor:
        user_columns = {
            column.name
            for column in connection.introspection.get_table_description(cursor, 'auth_user')
        }
        fields = (
            'id',
            'password',
            'last_login',
            'is_superuser',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_active',
            'date_joined',
        )
        selected_fields = [field for field in fields if field in user_columns]
        quoted_table = connection.ops.quote_name('auth_user')
        quoted_fields = ', '.join(connection.ops.quote_name(field) for field in selected_fields)
        cursor.execute(f'SELECT {quoted_fields} FROM {quoted_table}')
        users = []
        for row in cursor.fetchall():
            user_data = dict(zip(selected_fields, row))
            for field in ('last_login', 'date_joined'):
                value = user_data.get(field)
                if value is not None and timezone.is_naive(value):
                    user_data[field] = timezone.make_aware(value)
            users.append(User(**user_data))
    User.objects.using(alias).bulk_create(users)

    through_tables = (
        ('auth_user_groups', User.groups.through, 'group_id'),
        ('auth_user_user_permissions', User.user_permissions.through, 'permission_id'),
    )
    for table_name, through_model, related_field in through_tables:
        if table_name not in table_names:
            continue
        quoted_table = connection.ops.quote_name(table_name)
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT user_id, {connection.ops.quote_name(related_field)} '
                f'FROM {quoted_table}'
            )
            relations = [
                through_model(user_id=user_id, **{related_field: related_id})
                for user_id, related_id in cursor.fetchall()
            ]
        through_model.objects.using(alias).bulk_create(relations)

    with connection.cursor() as cursor:
        for statement in connection.ops.sequence_reset_sql(no_style(), [User]):
            cursor.execute(statement)


class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0001_initial'),
    ]

    run_before = [
        ('admin', '0002_logentry_remove_auto_add'),
    ]

    operations = [
        migrations.RunPython(copy_legacy_users, migrations.RunPython.noop),
    ]
