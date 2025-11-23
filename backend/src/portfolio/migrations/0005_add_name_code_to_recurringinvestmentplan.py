from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0004_recurringinvestmentplan_continue_if_limit_exceeded"),
    ]

    operations = [
        migrations.AddField(
            model_name="recurringinvestmentplan",
            name="target_asset_identifier",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="recurringinvestmentplan",
            name="target_asset_name",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
    ]
