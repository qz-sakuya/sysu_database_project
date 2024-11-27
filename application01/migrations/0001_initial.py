# Generated by Django 3.2.25 on 2024-11-26 10:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_data', models.BinaryField()),
                ('image_type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Line',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line_no', models.CharField(max_length=10, unique=True)),
                ('line_name', models.CharField(max_length=100, unique=True)),
                ('icon_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='application01.image')),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station_name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform_no', models.IntegerField()),
                ('line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application01.line')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application01.station')),
            ],
            options={
                'unique_together': {('line', 'station'), ('line', 'platform_no')},
            },
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_time', models.IntegerField()),
                ('out_station', models.BooleanField()),
                ('platforms_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='platforms_1_set', to='application01.platform')),
                ('platforms_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='platforms_2_set', to='application01.platform')),
            ],
            options={
                'unique_together': {('platforms_1', 'platforms_2')},
            },
        ),
        migrations.CreateModel(
            name='StationFacility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facility_type', models.CharField(max_length=50)),
                ('icon_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='application01.image')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application01.station')),
            ],
            options={
                'unique_together': {('station', 'facility_type')},
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section_no', models.IntegerField()),
                ('travel_time', models.IntegerField()),
                ('fare', models.DecimalField(decimal_places=2, max_digits=10)),
                ('line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application01.line')),
                ('platform1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='platform1_set', to='application01.platform')),
                ('platform2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='platform2_set', to='application01.platform')),
            ],
            options={
                'unique_together': {('line', 'section_no'), ('line', 'platform1', 'platform2')},
            },
        ),
        migrations.CreateModel(
            name='LastTrain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direction', models.CharField(max_length=10)),
                ('departure_time', models.TimeField()),
                ('platform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application01.platform')),
            ],
            options={
                'unique_together': {('platform', 'direction')},
            },
        ),
        migrations.CreateModel(
            name='FirstTrain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direction', models.CharField(max_length=10)),
                ('departure_time', models.TimeField()),
                ('platform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application01.platform')),
            ],
            options={
                'unique_together': {('platform', 'direction')},
            },
        ),
        migrations.CreateModel(
            name='Exit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exit_no', models.IntegerField()),
                ('exit_name', models.CharField(max_length=100)),
                ('exit_address', models.CharField(max_length=255)),
                ('exit_sub_address', models.CharField(blank=True, max_length=255, null=True)),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application01.station')),
            ],
            options={
                'unique_together': {('station', 'exit_name'), ('station', 'exit_no')},
            },
        ),
    ]
