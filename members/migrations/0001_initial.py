# Generated by Django 3.2.8 on 2021-10-13 18:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, unique=True)),
                ('slug', models.SlugField(max_length=250, unique=True)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(blank=True, upload_to='category')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Commitment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(blank=True, max_length=250)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='KES Committed Total')),
                ('name', models.CharField(blank=True, max_length=20)),
                ('email_address', models.EmailField(blank=True, max_length=250, verbose_name='Email Address')),
                ('phone_number', models.CharField(blank=True, max_length=250)),
                ('ministry', models.CharField(blank=True, max_length=20)),
                ('commitment_date', models.DateField()),
                ('deadline', models.DateField()),
            ],
            options={
                'db_table': 'Commitment',
                'ordering': ['-commitment_date'],
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, unique=True)),
                ('slug', models.SlugField(max_length=250, unique=True)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image', models.ImageField(blank=True, upload_to='item')),
                ('stock', models.IntegerField()),
                ('available', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.category')),
            ],
            options={
                'verbose_name': 'item',
                'verbose_name_plural': 'items',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Pledge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pledge_id', models.CharField(blank=True, max_length=250)),
                ('date_added', models.DateField(auto_now_add=True)),
            ],
            options={
                'db_table': 'Pledge',
                'ordering': ['date_added'],
            },
        ),
        migrations.CreateModel(
            name='PledgeItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('active', models.BooleanField(default=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.item')),
                ('pledge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.pledge')),
            ],
            options={
                'db_table': 'PledgeItem',
            },
        ),
        migrations.CreateModel(
            name='CommittedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=250)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='KES Price')),
                ('commitment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.commitment')),
            ],
            options={
                'db_table': 'CommittedItem',
            },
        ),
    ]
