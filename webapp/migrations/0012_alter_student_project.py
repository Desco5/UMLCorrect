# Generated by Django 4.1 on 2023-07-12 13:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0011_alter_student_project"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="project",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="webapp.project",
            ),
        ),
    ]