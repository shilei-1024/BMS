from django.shortcuts import render,HttpResponse,redirect
from django.contrib import auth
from django.http import JsonResponse
from django import forms
from django.forms import widgets as wid
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.db.models import Q
from django.urls import reverse
from django.views import View
from django.forms.models import modelformset_factory
from django.db.models import Count

import random
import re
import datetime

from app01.models import UserInfo, Customer, ConsultRecord, ClassStudyRecord, StudentStudyRecord, Student
from app01.page import Pagination

# Create your views here.
# ========== 原始基于forms组件的注册 ==========
# 注册
class UserForm(forms.Form):
    username = forms.CharField(max_length=32, label="用户名")
    password = forms.CharField(min_length=3, max_length=32, label="密码", widget=wid.PasswordInput())
    r_password = forms.CharField(min_length=3, max_length=32, label="确认密码", widget=wid.PasswordInput())
    email = forms.EmailField(max_length=32, label="邮箱")

    # 统一设置样式
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for filed in self.fields.values():
            filed.widget.attrs.update({'class': 'form-control'})

    # 用户不能重复
    def clean_username(self):
        val = self.cleaned_data.get("username")
        user = UserInfo.objects.filter(username=val).first()
        if user:
            raise ValidationError("用户已存在")
        else:
            return val

    # 密码不能是纯数字
    def clean_password(self):
        val = self.cleaned_data.get("password")
        if val.isdigit():
            raise ValidationError("密码不能是纯数字")
        else:
            return val

    # 邮箱必须是163邮箱
    def clean_email(self):
        val = self.cleaned_data.get("email")
        if re.search("\w+@163.com$", val):
            return val
        else:
            raise ValidationError("邮箱必须是163邮箱")

    # 两次密码不一致
    def clean(self):
        p1 = self.cleaned_data.get("password")
        p2 = self.cleaned_data.get("r_password")
        if p1 and p2 and p1 != p2:
            # 将错误信息直接写入到add_error中, 不用默认的__all__作为键, 使用自定的键, 方便后面的使用,
            # 也不用再对__all__做特殊化处理了(原因,看源码)
            self.add_error("r_password", ValidationError("两次密码不一致"))
            # raise ValidationError("两次密码不一致")
        else:
            return self.cleaned_data

def register(request):
    if request.is_ajax():
        # 绑定数据的表单实例
        form = UserForm(request.POST)
        response = {"username": None, "err_msg": ""}
        if form.is_valid():
            response["username"] = request.POST.get("username")
            username = request.POST.get("username")
            password = request.POST.get("password")
            UserInfo.objects.create_user(username=username, password=password)
        else:
            response["err_msg"] = form.errors
        return JsonResponse(response)
    else:
        form = UserForm()
        return render(request, "register.html", locals())

# ========== 基于modelform的注册 ==========
# 首先需要导入ModelForm类
class UserModelForm(ModelForm):
    class Meta:
        # 与models建立依赖关系
        model = UserInfo
        # 字段，__all__ 表示列出所有字段
        # fields = "__all__"
        fields = ['username', 'password', 'email']
        # 排除的字段
        exclude = None

        # 单独设置每个错误;
        # error_messages 全局设置, 所以加s
        error_messages = {
            "username": {'required': '用户名不能为空', },
            "password": {'required': '密码不能为空', },
            # "r_password": {'r_required': '确认密码不能为空'},
            "email": {'required': '邮件不能为空', },
        }

        labels = {
            "username": "用户名",
            "password": "密码",
            # "r_password": "确认密码",
            "email": "邮件",
        }

        widgets = {
            "password": wid.PasswordInput(),
            # "r_password": wid.PasswordInput(),
        }

    r_password = forms.CharField(min_length=3, max_length=32, label="确认密码", widget=wid.PasswordInput())
    # 统一设置样式
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for filed in self.fields.values():
            filed.widget.attrs.update({'class': 'form-control'})

    # 钩子的用法一致
    # 用户不能重复
    def clean_username(self):
        val = self.cleaned_data.get("username")
        user = UserInfo.objects.filter(username=val).first()
        if user:
            raise ValidationError("用户已存在")
        else:
            return val

    # 密码不能是纯数字
    def clean_password(self):
        val = self.cleaned_data.get("password")
        if val.isdigit():
            raise ValidationError("密码不能是纯数字")
        else:
            return val

    # 邮箱必须是163邮箱
    def clean_email(self):
        val = self.cleaned_data.get("email")
        if re.search("\w+@163.com$", val):
            return val
        else:
            raise ValidationError("邮箱必须是163邮箱")

    # 两次密码不一致
    def clean(self):
        p1 = self.cleaned_data.get("password")
        p2 = self.cleaned_data.get("r_password")
        if p1 and p2 and p1 != p2:
            # 将错误信息直接写入到add_error中, 不用默认的__all__作为键, 使用自定的键, 方便后面的使用,
            # 也不用再对__all__做特殊化处理了(原因,看源码)
            self.add_error("r_password", ValidationError("两次密码不一致"))
            # raise ValidationError("两次密码不一致")
        else:
            return self.cleaned_data

def model_register(request):
    if request.is_ajax():
        # 绑定数据的表单实例
        form = UserModelForm(request.POST)
        response = {"username": None, "err_msg": ""}
        if form.is_valid():
            response["username"] = request.POST.get("username")
            # 添加记录
            form.save()
        else:
            response["err_msg"] = form.errors
        return JsonResponse(response)
    else:
        form = UserModelForm()
        return render(request, "model_register.html", {'form': form})

# 登录
def login(request):
    if request.is_ajax():   # 判断是否是ajax发来的请求，布尔类型true或false
        username = request.POST.get("username")
        password = request.POST.get("password")
        validcode = request.POST.get("validcode")

        # Ajax请求返回一个字典
        response = {"username": None, "err_msg": ""}
        # request.session????????????????????
        if validcode.upper() == request.session.get("keep_str").upper():
            # auth.authenticate 用户认证，验证用户名及密码是否正确；没有返回None
            user_obj = auth.authenticate(username=username, password=password)
            if user_obj:
                response["username"] = username
                #
                auth.login(request, user_obj)
            else:
                response["err_msg"] = "用户名或者密码错误"
        else:
            response["err_msg"] = "验证码错误"
        # JsonResponse 自动将字典序列化, 并设置 Content-Type: application/json
        return JsonResponse(response)
    else:
        return render(request, "login.html")

# 验证码
def get_valid_img(request):
    # 依赖pil模块, 需要安装
    # pip3 install pillow
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO

    # 定义三原色的随机值
    def get_random_color():
        return (random.randint(0,255),random.randint(0,255),random.randint(0,255))

    # 获取一个img对象, 参数分别是RGB模式 宽350, 高38, 红色
    img = Image.new("RGB", (350, 38), get_random_color())

    # 获取一个画笔对象, 将图片对象传过去
    draw = ImageDraw.Draw(img)

    # 获取一个font字体对象, 参数是ttf的字体文件路径, 以及字体的大小
    font = ImageFont.truetype("static/font/kumo.ttf", 32)

    # 获取每次循环产生的验证码
    keep_str = ""

    # 生成6位的随机验证码
    for i in range(6):
        # 随机获取数字
        random_num = str(random.randint(0, 9))
        # 随机获取小写字母
        random_lowalf = chr(random.randint(97, 122))
        # 随机获取大写字母
        random_upperalf = chr(random.randint(65, 90))
        # 随机抽取一个值
        random_char = random.choice([random_num, random_lowalf,  random_upperalf])
        # text格式: text(self, xy, text, fill=None, font=None, anchor=None, *args, **kwargs), 看源码
        # 在图片上写东西, 参数是: 定位, 字符串, 颜色, 字体
        draw.text((i*30+80, 0), random_char, get_random_color(), font=font)
        keep_str += random_char

    # 在内存生成图片
    f = BytesIO()
    img.save(f, "png")
    data = f.getvalue()

    # 将验证码存在各自的session中
    request.session['keep_str'] = keep_str

    return HttpResponse(data)

# 首页
def index(request):
    return render(request, "index.html")

# 全部用户+批量删除/公转私
class Customers(View):
    # 查看数据
    def get(self, request):
        # reverse()反向解析，获取customers_list对应的url
        if reverse("customers_list") == request.path:
            label = "公开客户"
            # __isnull 查看销售是否为空,为空的表示公开客户
            customers_list = Customer.objects.filter(consultant__isnull=True)
        else:
            label = "我的客户"
            customers_list = Customer.objects.filter(consultant_id=request.user)

        # val 关键字
        # filed 根据 姓名/QQ/手机 那种类型过滤
        val = request.GET.get("q")
        field = request.GET.get("field")
        if val:
            # Q的实例对象
            q = Q()
            # 里面放元祖
            q.children.append((field + "__contains", val))
            customers_list = Customer.objects.filter(q)

        # 分页
        current_page_num = request.GET.get("page")
        pagination = Pagination(current_page_num, customers_list.count(), request)
        customers_list = customers_list[pagination.start: pagination.end]
        return render(request, "customer_list.html", {"customers_list": customers_list, "pagination": pagination, "label": label})

    # 批量操作
    def post(self, request):
        # 由于要用到反射, 将customers改为CBV的模式
        # func_str 不要和反射的函数名字一样
        func_str = request.POST.get("field")
        # 反射
        if hasattr(self, func_str):
            batch = getattr(self, func_str)
            select_list_pk = request.POST.get("select_list_pk")
            batch(request, select_list_pk)
            # 一定要写返回值, 不能再这里只写self.get(request)
            ret = self.get(request)
            return ret
        else:
            return HttpResponse("非法信息")

    # 批量删除调用的方法(这里是更新的操作, 数据珍贵, 不能随便删除)
    def batch_delet(self, select_list_pk):
        Customer.objects.filter(pk__in=select_list_pk).update(sex="male")

    # 公转私调用的方法
    def private_transfer(self, request, select_list_pk):
        # 获取登录用户在用户表中的id
        # user_pk = UserInfo.objects.filter(username=request.user).get("id")
        # 更新Customer的销售的id, ORM操作不熟悉, 上面那条语句, 不用写
        # 判断多个人对同一条数据操作时，第一个人选择，第二个人选择不会生效
        if Customer.objects.filter(Q(consultant__isnull=True) & Q(pk__in=select_list_pk)):
            Customer.objects.filter(pk__in=select_list_pk).update(consultant=request.user)
        else:
            return HttpResponse("手速慢")

    # 私转公调用的方法
    def transfer_private(self, request, select_list_pk):
        Customer.objects.filter(pk__in=select_list_pk).update(consultant=None)

# def customers(request):
#     if request.method == "GET":
#         val = request.GET.get("q")
#         field = request.GET.get("field")
#         if val:
#             # Q的实例对象
#             q = Q()
#             # 里面放元祖
#             q.children.append((field + "__contains", val))
#             customers_list = Customer.objects.filter(q)
#         else:
#             customers_list = Customer.objects.all()
#
#         # 分页
#         current_page_num = request.GET.get("page")
#         pagination = Pagination(current_page_num, customers_list.count(), request)
#         customers_list = customers_list[pagination.start: pagination.end]
#         return render(request, "customer_list.html", {"customers_list": customers_list, "pagination": pagination})
#     else:
#         # 由于要用到反射, 将customers改为CBV的模式
#         batch_delet = request.POST.get("field")
#         select_list_pk = request.POST.get("select_list_pk")
#         print(batch_delet, select_list_pk)
#         return HttpResponse("OK")

# 私有用户
# 私有客户
def mycustomers(request):
    customers_list = Customer.objects.filter(consultant_id=request.user.pk)
    val = request.GET.get("q")
    field = request.GET.get("field")
    if val:
        # Q的实例对象
        q = Q()
        # 里面放元祖
        q.children.append((field + "__contains", val))
        customers_list = Customer.objects.filter(q)

    # 分页
    current_page_num = request.GET.get("page")
    pagination = Pagination(current_page_num, customers_list.count(), request)
    customers_list = customers_list[pagination.start: pagination.end]
    return render(request, "mycustomer_list.html", {"customers_list": customers_list, "pagination": pagination})

# 添加客户
class CustomerModelForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"

    # 格式化
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            from multiselectfield.forms.fields import MultiSelectFormField
            if not isinstance(field,MultiSelectFormField):
                field.widget.attrs.update({'class': 'form-control'})

# 添加/编辑数据
class AddEditCustomers(View):
    def get(self, request, edit_id=None):
        # instance = 对象, 填写默认值
        # get取值，为空会报错，用first不会报错
        # eidt_obj = Customer.objects.get(pk=edit_id)
        eidt_obj = Customer.objects.filter(pk=edit_id).first()
        customer_list = CustomerModelForm(instance=eidt_obj)
        return render(request, "add_edit_customer.html", {'customer_list': customer_list})

    def post(self, request, edit_id=None):
        # 这里的instance用来说明是更新操作, 而不是新添加一条数据
        eidt_obj = Customer.objects.filter(pk=edit_id).first()
        customer_list = CustomerModelForm(request.POST, instance=eidt_obj)
        if customer_list.is_valid():
            customer_list.save()
            return redirect("/customers/list/")
        else:
            return render(request, "add_edit_customer.html", {'customer_list': customer_list})

# 删除
class DelCustomers(View):
    def get(self, request, id):
        # instance = 对象, 填写默认值
        Customer.objects.get(pk=id).delete()
        return redirect("/customers/list/")

# 客户跟踪记录
class TrackCustomers(View):
    def get(self, request):
        customer_list = ConsultRecord.objects.filter(consultant=request.user)
        customer_id = request.GET.get("customer_id")
        if customer_id:
            customer_list = ConsultRecord.objects.filter(customer_id=customer_id)
        return render(request, "track_customer_list.html", {"customer_list": customer_list})

# 客户跟踪记录--添加
class AddTrackModelForm(forms.ModelForm):
    class Meta:
        model = ConsultRecord
        # fields = "__all__"
        exclude = ['delete_status']

    # 格式化
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            # from multiselectfield.forms.fields import MultiSelectFormField
            # if not isinstance(field,MultiSelectFormField):
            field.widget.attrs.update({'class': 'form-control'})

# 客户跟踪记录添加/编辑
class AddEditTrackCustomers(View):
    def get(self, request, edit_id=None):
        edit_obj = ConsultRecord.objects.filter(pk=edit_id).first()
        customer_list = AddTrackModelForm(instance=edit_obj)
        return render(request, "add_edit_track_customer.html", {'customer_list': customer_list})

    def post(self, request, edit_id=None):
        edit_obj = ConsultRecord.objects.filter(pk=edit_id).first()
        customer_list = AddTrackModelForm(request.POST, instance=edit_obj)
        if customer_list.is_valid():
            customer_list.save()
            return redirect("/customers/tracking/")
        else:
            return render(request, "add_edit_track_customer.html", {'customer_list': customer_list})

# 班级学习记录/批量添加学生记录
class ClassStudyList(View):
    def get(self, request):
        class_list = ClassStudyRecord.objects.all()
        return render(request, 'class_study_list.html', locals())

    def post(self, request):
        field = request.POST.get("field")
        if hasattr(self, field):
            batch = getattr(self, field)
            pk_list = request.POST.getlist("select_list_pk")
            batch(pk_list)
        return redirect("/class/study/list/")

    # 批量添加学生记录
    def batch_student_add(self, pk_list):
        for pk in pk_list:
            cls = ClassStudyRecord.objects.filter(pk=pk).first().class_obj
            stu = Student.objects.filter(class_list=cls).values("pk")
            for item in stu:
                student = item['pk']
                StudentStudyRecord.objects.create(student_id=student, classstudyrecord_id=pk)
    # 批量删除学生记录
    def batch_student_del(self, pk_list):
        for pk in pk_list:
            cls = ClassStudyRecord.objects.filter(pk=pk).first().class_obj
            stu = Student.objects.filter(class_list=cls).values("pk")
            for item in stu:
                student = item['pk']
                StudentStudyRecord.objects.filter(student_id=student, classstudyrecord_id=pk).delete()

# 班级跟踪记录添加/编辑
class AddClassStudyModelFrom(forms.ModelForm):
    class Meta:
        model = ClassStudyRecord
        fields = "__all__"

        # 格式化
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                from multiselectfield.forms.fields import MultiSelectFormField
                if not isinstance(field, MultiSelectFormField):
                    field.widget.attrs.update({'class': 'form-control'})

# 班级跟踪记录添加/编辑
class AddEditClassStudy(View):
    def get(self, request, edit_id=None):
        edit_obj = ClassStudyRecord.objects.filter(pk=edit_id).first()
        class_list = AddClassStudyModelFrom(instance=edit_obj)
        return render(request, "add_edit_class_study.html", {"class_list": class_list})
    def post(self, request, edit_id=None):
        edit_obj = ClassStudyRecord.objects.filter(pk=edit_id).first()
        class_list = AddClassStudyModelFrom(request.POST, instance=edit_obj)
        if class_list.is_valid():
            class_list.save()
            return redirect("/class/study/list/")
        else:
            return render(request, "add_edit_class_study.html", {'class_list': class_list})

# 班级跟踪记录删除
class DelClassStudy(View):
    def get(self, request, edit_id=None):
        ClassStudyRecord.objects.filter(pk=edit_id).delete()
        return redirect("/class/study/list/")

# 班级跟踪记录-录入成绩
class RecordEntry2(View):
    def get(self, request, edit_id):
        class_obj = ClassStudyRecord.objects.get(pk=edit_id)
        student_list = class_obj.studentstudyrecord_set.all()
        return render(request, "record_entry.html", {"student_list": student_list})
    def post(self,request, edit_id):
        class_obj = ClassStudyRecord.objects.get(pk=edit_id)
        student_list = class_obj.studentstudyrecord_set.all()
        for student in student_list:
            pk = student.pk
            score = request.POST.get('score_{}'.format(pk))
            homework_note = request.POST.get('homework_note_{}'.format(pk))
            StudentStudyRecord.objects.filter(pk=pk).update(score=score,
                                              homework_note=homework_note,
                                              )
        return self.get(request, edit_id)

# 班级跟踪记录-录入成绩(modelformset)
class StudentStudyRecordModelForm(forms.ModelForm):
    class Meta:
        model = StudentStudyRecord
        #
        fields = ["score", "homework_note"]

class RecordEntry(View):
    def get(self, request, edit_id):
        # model 跟那个模型；form 跟ModelForm
        # extra 可以添加数据，等于几，就可以添加几个，默认等于1，我们这里只是选择数据，所以置为0
        model_formset_cls = modelformset_factory(model=StudentStudyRecord,
                                                 form=StudentStudyRecordModelForm,
                                                 extra=0)
        queryset = StudentStudyRecord.objects.filter(classstudyrecord=edit_id)
        formset = model_formset_cls(queryset=queryset)
        return render(request, "record_entry.html", locals())
    def post(self, request, edit_id):
        model_formset_cls = modelformset_factory(model=StudentStudyRecord,
                                                 form=StudentStudyRecordModelForm,
                                                 extra=0)
        formset = model_formset_cls(request.POST)
        # form,modelform, modelformset 都有is_valid这个方法
        # is_valid在校验是， 会根据fields写的字段进行校验，所以不要写__all__，用到那个， 写那个字段
        if formset.is_valid():
            formset.save()
        return redirect(request.path)

# 学生学习记录
class StudentStudyList(View):
    def get(self, request):
        student_list = StudentStudyRecord.objects.all()
        return render(request, 'student_study_list.html', locals())

# 学生学习记录添加/编辑
class StudentStudyModelFrom(forms.ModelForm):
    class Meta:
        model = StudentStudyRecord
        fields = "__all__"

        # 格式化
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                from multiselectfield.forms.fields import MultiSelectFormField
                if not isinstance(field, MultiSelectFormField):
                    field.widget.attrs.update({'class': 'form-control'})

# 学生学习记录添加/编辑
class AddEditStudentStudy(View):
    def get(self, request, edit_id=None):
        edit_obj = StudentStudyRecord.objects.filter(pk=edit_id).first()
        student_list = StudentStudyModelFrom(instance=edit_obj)
        return render(request, "add_edit_student_study.html", {"student_list": student_list})
    def post(self, request, edit_id=None):
        edit_obj = StudentStudyRecord.objects.filter(pk=edit_id).first()
        student_list = StudentStudyModelFrom(request.POST, instance=edit_obj)
        if student_list.is_valid():
            student_list.save()
            return redirect("/student/study/list/")
        else:
            return render(request, "add_edit_student_study.html", {'student_list': student_list})

# 学生学习记录删除
class DelStudentStudy(View):
    def get(self, request, edit_id=None):
        StudentStudyRecord.objects.filter(pk=edit_id).delete()
        return redirect("/student/study/list/")

# 统计查询
class CountQueryView(View):
    def get(self, request):
        # 给个默认值，today
        date = request.GET.get("date", "today")
        if hasattr(self, date):
            val = getattr(self, date)()
        return render(request, 'count_query.html', val)
    def today(self):
        now = datetime.datetime.now().date()
        customer_list = Customer.objects.filter(deal_date=now)
        # 查询每一个销售的名字以及今天对应的成单量
        ret = UserInfo.objects.filter(depart_id=1, customers__deal_date=now).annotate(c=Count("customers")).values_list("username","c")
        # 列表表达式
        ret = [[item[0], item[1]] for item in list(ret)]
        return {"customer_list": customer_list, "ret": ret}

    def yesterday(self):
        now = datetime.datetime.now().date()
        date = now - datetime.timedelta(days=1)
        customer_list = Customer.objects.filter(deal_date=date)
        # 查询每一个销售的名字以及昨天的成单量
        ret = UserInfo.objects.filter(depart_id=1, customers__deal_date=date).annotate(c=Count("customers")).values_list("username","c")
        # 列表表达式
        ret = [[item[0], item[1]] for item in list(ret)]
        return {"customer_list": customer_list, "ret": ret}

    def week(self):
        now = datetime.datetime.now().date()
        date = now - datetime.timedelta(weeks=1)
        customer_list = Customer.objects.filter(deal_date__gte=date)
        # 查询每一个销售的名字以及最近一周的成单量
        ret = UserInfo.objects.filter(depart_id=1, customers__deal_date__gte=date).annotate(c=Count("customers")).values_list("username","c")
        # 列表表达式
        ret = [[item[0], item[1]] for item in list(ret)]
        return {"customer_list": customer_list, "ret": ret}

    def month(self):
        now = datetime.datetime.now().date()
        date = now - datetime.timedelta(weeks=4)
        customer_list = Customer.objects.filter(deal_date__gte=date)
        # 查询每一个销售的名字以及最近一周的成单量
        ret = UserInfo.objects.filter(depart_id=1, customers__deal_date__gte=date).annotate(c=Count("customers")).values_list("username","c")
        # 列表表达式
        ret = [[item[0], item[1]] for item in list(ret)]
        return {"customer_list": customer_list, "ret": ret}

