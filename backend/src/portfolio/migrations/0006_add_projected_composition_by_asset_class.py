from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0005_add_name_code_to_recurringinvestmentplan"),
    ]

    operations = [
        migrations.AddField(
            model_name="projection",
            name="projected_composition_by_asset_class",
            field=models.TextField(default="", help_text="JSON string of asset-class-wise composition"),
        ),
    ]
