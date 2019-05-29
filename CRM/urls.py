"""CRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from app01 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # 登陆
    path('login/', views.login),
    # 验证码
    path('get_valid_img/', views.get_valid_img),
    # 注册
    path('register/', views.register),
    # 基于modelForm的实现的注册功能
    path('model_register/', views.model_register),
    # 访问首页
    path('index/', views.index),
    # 访问公开用户; name 别名
    path('customers/list/', views.Customers.as_view(), name="customers_list"),
    # 访问私有用户
    # path('mycustomers/list/', views.mycustomers, name="mycustomers_list"),
    path('mycustomers/list/', views.Customers.as_view(), name="mycustomers_list"),
    # 添加公共客户
    path('customers/add/', views.AddEditCustomers.as_view(), name="add_customers"),
    # 编辑公共客户, 使用re_path
    re_path('^customers/edit/(\d+)/$', views.AddEditCustomers.as_view(), name="edit_customers"),
    # 删除公共客户, 使用re_path
    re_path('^customers/del/(\d+)/$', views.DelCustomers.as_view(), name="del_customers"),
    # 客户跟踪记录
    path('customers/tracking/', views.TrackCustomers.as_view(), name="track_customers"),
    # 添加客户跟踪记录
    path('track_customers/add/', views.AddEditTrackCustomers.as_view(), name="add_track_customers"),
    # 编辑客户跟踪记录
    re_path('^track_customers/edit/(\d+)/$', views.AddEditTrackCustomers.as_view(), name="edit_track_customers"),
    # 班级跟踪记录
    path('class/study/list/', views.ClassStudyList.as_view(), name="class_study_list"),
    # 班级跟踪记录-添加
    path('class/study/add/', views.AddEditClassStudy.as_view(), name="add_class_study"),
    # 班级跟踪记录-编辑
    re_path('^class/study/edit/(\d+)/$', views.AddEditClassStudy.as_view(), name="add_class_study"),
    # 班级跟踪记录-删除
    re_path('^class/study/del/(\d+)/$', views.DelClassStudy.as_view(), name="del_class_study"),
    # 班级跟踪记录-录入成绩
    re_path('^record/entry/(\d+)/$', views.RecordEntry.as_view(), name="record_entry"),
    # 学生学习记录
    path('student/study/list/', views.StudentStudyList.as_view(), name="student_study_list"),
    # 学生学习记录-添加
    path('student/study/add/', views.AddEditStudentStudy.as_view(), name="add_study_list"),
    # 学生学习记录-编辑
    re_path('student/study/edit/(\d+)/$', views.AddEditStudentStudy.as_view(), name="edit_study_list"),
    # 学生学习记录-删除
    re_path('student/study/del/(\d+)/$', views.DelStudentStudy.as_view(), name="del_study_list"),
    # 统计查询
    path('count_query/', views.CountQueryView.as_view(), name="count_query"),
]
