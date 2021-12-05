# Generated by Django 3.2.9 on 2021-12-05 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registers', '0002_register_new_dataset'),
    ]

    operations = [
        migrations.CreateModel(
            name='AWSConstants',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('album_bucket_name', models.CharField(help_text='Please refrain from adding more objects. Just edit the current one', max_length=100)),
                ('bucket_region', models.CharField(max_length=50)),
                ('identity_pool_id', models.CharField(max_length=150)),
                ('lambda_function_url', models.URLField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'AWS Constant',
                'verbose_name_plural': 'AWS Constants',
            },
        ),
        migrations.AlterField(
            model_name='register',
            name='new_dataset',
            field=models.JSONField(default=dict, help_text='Generated file from the classification category'),
        ),
        migrations.AlterField(
            model_name='register',
            name='target_column',
            field=models.CharField(help_text='*Optional', max_length=55),
        ),
    ]