# Generated by Django 4.1 on 2023-06-29 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0005_project_dir"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="class_name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="project",
            name="deadline",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="project",
            name="project_name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="project",
            name="publication_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="project",
            name="solutions_sent",
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="project",
            name="solutions_total",
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="student",
            name="score",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=4, null=True
            ),
        ),
    ]