from django.db import migrations


def wipe_comments(apps, schema_editor):
    # Comments were attached to variants, which no longer exist.
    apps.get_model("review", "CommentImage").objects.all().delete()
    apps.get_model("review", "Comment").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("review", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(wipe_comments, migrations.RunPython.noop),
    ]
