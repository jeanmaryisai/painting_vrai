# Generated by Django 5.0.7 on 2024-08-24 18:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivacyPolicy_paragraph',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('paragraph', models.TextField()),
                ('Settings', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.setting')),
            ],
        ),
        migrations.CreateModel(
            name='TermsAndConditions_paragraph',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('paragraph', models.TextField()),
                ('Settings', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.setting')),
            ],
        ),
    ]
