from django.db import migrations, models


def merge_roles(apps, schema_editor):
    # Only clients and admins remain; staff-like roles become admins.
    apps.get_model("authentication", "User").objects.filter(
        role__in=["seller", "moderator", "super_admin"]
    ).update(role="admin")


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0007_remove_user_currency"),
    ]

    operations = [
        migrations.RunPython(merge_roles, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[("buyer", "Client"), ("admin", "Admin")], default="buyer"
            ),
        ),
    ]
