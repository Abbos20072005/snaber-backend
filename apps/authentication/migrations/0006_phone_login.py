from django.db import migrations, models

import apps.authentication.utils


def blank_to_null(apps, schema_editor):
    User = apps.get_model("authentication", "User")
    User.objects.filter(email="").update(email=None)
    User.objects.filter(phone_number="").update(phone_number=None)


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0005_user_country"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                blank=True,
                max_length=14,
                null=True,
                validators=[apps.authentication.utils.validate_number],
            ),
        ),
        migrations.RunPython(blank_to_null, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                blank=True,
                max_length=14,
                null=True,
                unique=True,
                validators=[apps.authentication.utils.validate_number],
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="full_name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="user",
            name="password",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
