# Generated by Django 3.2.19 on 2023-06-25 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Posts', '0008_auto_20230625_1400'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mediafile',
            name='encoding_task',
        ),
        migrations.AlterField(
            model_name='mediafile',
            name='file',
            field=models.FileField(blank=True, upload_to='media/postsMedia'),
        ),
    ]
