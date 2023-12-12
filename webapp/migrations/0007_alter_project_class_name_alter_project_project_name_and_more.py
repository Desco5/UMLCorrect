# Generated by Django 4.1 on 2023-06-29 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0006_alter_project_class_name_alter_project_deadline_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="class_name",
            field=models.CharField(default="Not defined", max_length=100),
        ),
        migrations.AlterField(
            model_name="project",
            name="project_name",
            field=models.CharField(default="New Project 1", max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="project",
            name="solutions_sent",
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="project",
            name="solutions_total",
            field=models.SmallIntegerField(default=0),
        ),
    ]
