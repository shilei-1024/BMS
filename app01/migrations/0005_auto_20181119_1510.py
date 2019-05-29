# Generated by Django 2.1.3 on 2018-11-19 07:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0004_auto_20181112_1746'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassStudyRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_num', models.IntegerField(help_text='此处填写第几节课或第几天课程...,必须为数字', verbose_name='节次')),
                ('date', models.DateField(auto_now_add=True, verbose_name='上课日期')),
                ('course_title', models.CharField(blank=True, max_length=64, null=True, verbose_name='本节课程标题')),
                ('course_memo', models.TextField(blank=True, null=True, verbose_name='本节课程内容概要')),
                ('has_homework', models.BooleanField(default=True, verbose_name='本节有作业')),
                ('homework_title', models.CharField(blank=True, max_length=64, null=True, verbose_name='本节作业标题')),
                ('homework_memo', models.TextField(blank=True, max_length=500, null=True, verbose_name='作业描述')),
                ('exam', models.TextField(blank=True, max_length=300, null=True, verbose_name='踩分点')),
                ('class_obj', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.ClassList', verbose_name='班级')),
                ('teacher', models.ForeignKey(limit_choices_to={'depart_id__in': [1002, 1003]}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='讲师')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emergency_contract', models.CharField(blank=True, max_length=32, null=True, verbose_name='紧急联系人')),
                ('company', models.CharField(blank=True, max_length=128, null=True, verbose_name='公司')),
                ('location', models.CharField(blank=True, max_length=64, null=True, verbose_name='所在区域')),
                ('position', models.CharField(blank=True, max_length=64, null=True, verbose_name='岗位')),
                ('salary', models.IntegerField(blank=True, null=True, verbose_name='薪资')),
                ('welfare', models.CharField(blank=True, max_length=256, null=True, verbose_name='福利')),
                ('date', models.DateField(blank=True, help_text='格式yyyy-mm-dd', null=True, verbose_name='入职时间')),
                ('memo', models.CharField(blank=True, max_length=256, null=True, verbose_name='备注')),
                ('class_list', models.ManyToManyField(blank=True, to='app01.ClassList', verbose_name='已报班级')),
            ],
        ),
        migrations.CreateModel(
            name='StudentStudyRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record', models.CharField(choices=[('checked', '已签到'), ('vacate', '请假'), ('late', '迟到'), ('noshow', '缺勤'), ('leave_early', '早退')], default='checked', max_length=64, verbose_name='上课纪录')),
                ('score', models.IntegerField(choices=[(100, 'A+'), (90, 'A'), (85, 'B+'), (80, 'B'), (70, 'B-'), (60, 'C+'), (50, 'C'), (40, 'C-'), (0, ' D'), (-1, 'N/A'), (-100, 'COPY'), (-1000, 'FAIL')], default=-1, verbose_name='本节成绩')),
                ('homework_note', models.CharField(blank=True, max_length=255, null=True, verbose_name='作业评语')),
                ('note', models.CharField(blank=True, max_length=255, null=True, verbose_name='备注')),
                ('homework', models.FileField(blank=True, default=None, null=True, upload_to='', verbose_name='作业文件')),
                ('stu_memo', models.TextField(blank=True, null=True, verbose_name='学员备注')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='提交作业日期')),
                ('classstudyrecord', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.ClassStudyRecord', verbose_name='第几天课程')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.Student', verbose_name='学员')),
            ],
        ),
        migrations.AlterField(
            model_name='consultrecord',
            name='consultant',
            field=models.ForeignKey(limit_choices_to={'pk': 9}, on_delete=django.db.models.deletion.CASCADE, related_name='records', to=settings.AUTH_USER_MODEL, verbose_name='跟进人'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='consultant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customers', to=settings.AUTH_USER_MODEL, verbose_name='销售'),
        ),
        migrations.AddField(
            model_name='student',
            name='customer',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app01.Customer', verbose_name='客户信息'),
        ),
    ]