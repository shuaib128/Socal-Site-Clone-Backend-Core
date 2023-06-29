# Generated by Django 3.2.13 on 2023-06-12 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Posts', '0003_auto_20230605_1240'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-date_created']},
        ),
        migrations.AddField(
            model_name='mediafile',
            name='filename',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='mediafile',
            name='temp_files',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
