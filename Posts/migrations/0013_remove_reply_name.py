# Generated by Django 3.2.19 on 2023-07-06 19:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Posts', '0012_comment_likes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reply',
            name='name',
        ),
    ]
