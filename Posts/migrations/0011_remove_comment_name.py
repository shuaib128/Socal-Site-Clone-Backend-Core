# Generated by Django 3.2.19 on 2023-07-03 07:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Posts', '0010_post_likes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='name',
        ),
    ]
