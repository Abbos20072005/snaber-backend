from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0006_phone_login"),
    ]

    operations = [
        migrations.RemoveField(model_name="user", name="currency"),
    ]
