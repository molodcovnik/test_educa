# Generated by Django 5.0.2 on 2024-02-28 20:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='lesson',
            unique_together={('lesson_name', 'product')},
        ),
    ]