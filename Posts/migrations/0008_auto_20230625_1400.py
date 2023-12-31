# Generated by Django 3.2.19 on 2023-06-25 21:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('background_task', '0003_auto_20230625_1358'),
        ('Posts', '0007_alter_mediafile_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediafile',
            name='encoding_task',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='background_task.task'),
        ),
        migrations.AddField(
            model_name='mediafile',
            name='hls_directory',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
