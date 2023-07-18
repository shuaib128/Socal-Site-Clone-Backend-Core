# Generated by Django 3.2.19 on 2023-06-29 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0001_initial'),
        ('Posts', '0009_auto_20230625_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.ManyToManyField(blank=True, null=True, related_name='likes', to='Users.Profile'),
        ),
    ]
