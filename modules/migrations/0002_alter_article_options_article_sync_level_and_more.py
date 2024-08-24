# Generated by Django 4.2 on 2024-08-24 03:14

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("modules", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="article",
            options={"ordering": ["-title"]},
        ),
        migrations.AddField(
            model_name="article",
            name="sync_level",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="article",
            name="sync_suggestion",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="article",
            name="content",
            field=ckeditor.fields.RichTextField(),
        ),
    ]
