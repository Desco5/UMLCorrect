# Generated by Django 4.1 on 2023-07-11 14:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0010_project_students_file_alter_project_dir_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="project",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="webapp.project",
            ),
        ),
    ]
