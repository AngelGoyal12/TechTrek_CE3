# Generated by Django 5.2 on 2025-05-04 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courseApp', '0004_testimonial'),
    ]

    operations = [
        migrations.AddField(
            model_name='testimonial',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='student_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
