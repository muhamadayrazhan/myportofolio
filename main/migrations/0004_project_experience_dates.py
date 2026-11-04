import uuid

import django.utils.timezone
from django.db import migrations, models

# SQLite rebuilds the table on AlterField by copying the raw text, so the old
# "2026-09-09 08:59:31.273687" values would stay in what is now a DateField.
TRIM_DATETIMES = """
UPDATE main_experience
   SET started_at = substr(started_at, 1, 10)
 WHERE started_at IS NOT NULL AND length(started_at) > 10;
UPDATE main_experience
   SET ended_at = substr(ended_at, 1, 10)
 WHERE ended_at IS NOT NULL AND length(ended_at) > 10;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_education_institution_image_url_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("web", "Web Development"),
                            ("mobile", "Mobile Development"),
                            ("data", "Data & Machine Learning"),
                            ("game", "Game Development"),
                            ("other", "Lainnya"),
                        ],
                        default="web",
                        max_length=20,
                    ),
                ),
                ("tech_stack", models.CharField(max_length=255)),
                ("project_url", models.URLField(blank=True)),
                ("project_image_url", models.URLField(blank=True, max_length=500)),
                ("year", models.PositiveIntegerField()),
                ("is_featured", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-is_featured", "-year", "title"],
            },
        ),
        migrations.AlterModelOptions(
            name="experience",
            options={"ordering": ["-started_at", "title"]},
        ),
        migrations.AddField(
            model_name="experience",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="experience",
            name="started_at",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="experience",
            name="ended_at",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RunSQL(TRIM_DATETIMES, migrations.RunSQL.noop),
    ]
