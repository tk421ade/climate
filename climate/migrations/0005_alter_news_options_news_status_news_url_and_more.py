# Generated by Django 5.0.4 on 2024-04-27 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climate', '0004_merge_0002_initial_0003_auto_20240427_0341'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='news',
            options={'verbose_name': 'News', 'verbose_name_plural': 'News'},
        ),
        migrations.AddField(
            model_name='news',
            name='status',
            field=models.CharField(choices=[('NEW', 'NEW'), ('MAIN', 'MAIN'), ('DISCARDED', 'DISCARDED')], default='NEW', max_length=10),
        ),
        migrations.AddField(
            model_name='news',
            name='url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='news',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]