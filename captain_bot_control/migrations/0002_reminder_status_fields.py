# Generated manually to introduce reminder status tracking fields.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('captain_bot_control', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reminder',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reminder',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='reminder',
            name='preserve_after_trigger',
            field=models.BooleanField(default=False),
        ),
    ]
