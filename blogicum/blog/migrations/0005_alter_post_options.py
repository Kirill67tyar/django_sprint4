# Generated by Django 3.2.16 on 2023-12-25 19:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'default_related_name': 'posts', 'ordering': ('-pub_date', 'title'), 'verbose_name': 'публикация', 'verbose_name_plural': 'Публикации'},
        ),
    ]
