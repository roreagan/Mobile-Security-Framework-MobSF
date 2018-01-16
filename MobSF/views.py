# -*- coding: utf_8 -*-
"""
MobSF File Upload and Home Routes
"""
import os
import hashlib
import shutil
import platform
import json
import re
import time
import threading

import tasks

from wsgiref.util import FileWrapper
from django.shortcuts import render
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.http import HttpResponseRedirect
from django.conf import settings
from django.utils import timezone
from django.forms.models import model_to_dict
from MobSF.utils import (
    print_n_send_error_response,
    PrintException,
    isDirExists,
    isFileExists,
    api_key
)
from MobSF.models import (
    RecentScansDB,
    Sample,
    Task,
    # User
)
from APITester.models import ScopeURLSandTests
from StaticAnalyzer.models import (
    StaticAnalyzerAndroid,
    StaticAnalyzerIPA,
    StaticAnalyzerIOSZIP,
    StaticAnalyzerWindows,
)
from DynamicAnalyzer.models import ManualAnalyzerAndroid
from StaticAnalyzer.views.android.db_interaction import get_context_from_db_entry
from .forms import (
    UploadFileForm,
    UploadTaskForm
)

from context import generate_dynamic_html



def add_to_recent_scan(name, md5, url):
    """
    Add Entry to Database under Recent Scan
    """
    try:
        db_obj = RecentScansDB.objects.filter(MD5=md5)
        if not db_obj.exists():
            new_db_obj = RecentScansDB(
                NAME=name, MD5=md5, URL=url, TS=timezone.now())
            new_db_obj.save()
    except:
        PrintException("[ERROR] Adding Scan URL to Database")


def add_to_sample(name, type, source, extra, md5):
    """
    Add Entry to Database under Sample
    """
    try:
        db_obj = Sample.objects.filter(MD5=md5)
        if not db_obj.exists():
            new_db_obj = Sample(
                NAME=name, TYPE=type, SOURCE=source, EXTRA=extra, MD5=md5, TS=timezone.now())
            new_db_obj.save()
            return True
        else:
            return False
    except:
        PrintException("[ERROR] Adding Scan URL to Database")
        return False


def index(request):
    """
    Index Route
    """
    # is_login = request.session.get('IS_LOGIN', False)
    is_login = True
    if is_login:
        username = request.session.get('USRNAME', False)
        return render(request, 'general/index_new.html', {'username': username, 'version': settings.MOBSF_VER})
    else:
        return HttpResponseRedirect('/login/')


def loginVerify(request):
    if request.method == 'POST':
        #获取表单用户密码
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if username == "admin":

            if "admin" == password:
                request.session['IS_LOGIN'] = True
                request.session['USRNAME'] = username
                return HttpResponse('1')
            else:
            #比较失败，还在login
                return HttpResponse('0')
        else:
            return HttpResponse('0')
    else:
        return render(request, 'general/login_new.html', {'version': settings.MOBSF_VER})


def login(request):
    is_login = request.session.get('IS_LOGIN', False)
    if is_login:
        username = request.session.get('USRNAME', False)
        return render(request, 'general/index_new.html', {'username': username, 'version': settings.MOBSF_VER})
    else:
        context = {'version': settings.MOBSF_VER}
        template = "general/login_new.html"
        return render(request, template, context)


def logout(request):
    request.session['IS_LOGIN'] = False
    request.session['USRNAME'] = ''
    return HttpResponseRedirect('/login/')


def samples(request):
    context = {'version': settings.MOBSF_VER}
    template = "general/samples.html"
    return render(request, template, context)


def task_html(request):
    context = {'version': settings.MOBSF_VER}
    template = "general/tasks.html"
    return render(request, template, context)


def up_tasks(request):
    context = {'version': settings.MOBSF_VER}
    template = "dynamic_analysis/manual_analysis.html"
    return render(request, template, context)


def static_feature(request):
    context = {'version': settings.MOBSF_VER}
    template = "general/static_feature.html"
    return render(request, template, context)


def script_feature(request):
    context = {'version': settings.MOBSF_VER}
    template = "general/script_feature.html"
    return render(request, template, context)


def manual_analysis(request):
    context = {'version': settings.MOBSF_VER}
    template = "dynamic_analysis/manual_analysis.html"
    return render(request, template, context)


def handle_uploaded_file(filecnt, typ):
    """
    Write Uploaded File
    """
    md5 = hashlib.md5()  # modify if crash for large
    for chunk in filecnt.chunks():
        md5.update(chunk)
    md5sum = md5.hexdigest()
    anal_dir = os.path.join(settings.UPLD_DIR, md5sum + '/')
    if not os.path.exists(anal_dir):
        os.makedirs(anal_dir)
    with open(anal_dir + md5sum + typ, 'wb+') as destination:
        for chunk in filecnt.chunks():
            destination.write(chunk)
    shutil.copy(anal_dir + md5sum + typ, settings.DWD_DIR + md5sum + typ)
    return md5sum


def upload_sample(request, api=False):
    """
        Handle File Upload
        """
    response_data = {}
    response_data['description'] = ''
    response_data['status'] = 'error'
    try:
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                file_type = request.FILES['file'].content_type
                print "[INFO] MIME Type: " + file_type + " FILE: " + request.FILES['file'].name
                if ((file_type in settings.APK_MIME) and
                        request.FILES['file'].name.lower().endswith('.apk')):
                    # APK
                    md5 = handle_uploaded_file(request.FILES['file'], '.apk')
                    response_data['status'] = 'success'
                    response_data['description'] = '文件添加成功'
                    if(add_to_sample(request.POST['name'], request.POST['type'], request.POST['source'],
                                     request.POST['extra'], md5) is not True):
                        response_data['description'] = '该文件已存在'
                    print "\n[INFO] Storing Android APK"
                else:
                    response_data['description'] = 'File format not Supported!'
                    response_data['status'] = 'error'
                    print "\n[ERROR] File format not Supported!"

            else:
                response_data['description'] = 'Invalid Form Data!'
                response_data['status'] = 'error'
                print "\n[ERROR] Invalid Form Data!"
        else:
            response_data['description'] = 'Method not Supported!'
            response_data['status'] = 'error'
            print "\n[ERROR] Method not Supported!"
    except:
        PrintException("[ERROR] Uploading File:")
    if response_data['status'] == 'error':
        resp = HttpResponse(json.dumps(
            response_data), content_type="application/json; charset=utf-8", status=500)
    else:
        resp = HttpResponse(json.dumps(response_data),
                            content_type="application/json; charset=utf-8")
    resp['Access-Control-Allow-Origin'] = '*'
    return resp


def get_samples(request):
    response_data = {}
    response_data['status'] = 'success'
    sampless = Sample.objects.all()
    sams = []
    for i in sampless:
        temp = {}
        temp['name'] = i.NAME
        temp['type'] = i.TYPE
        temp['source'] = i.SOURCE
        temp['extra'] = i.EXTRA
        temp['md5'] = i.MD5
        temp['TS'] = '{}-{}-{} {}:{}:{}'.format(i.TS.year, i.TS.month, i.TS.day, i.TS.hour, i.TS.minute, i.TS.second)
        sams.append(temp)
    response_data['samples'] = sams
    return HttpResponse(json.dumps(response_data), content_type="application/json; charset=utf-8")


def delete_sample(request):
    try:
        Sample.objects.get(MD5=request.GET['md5']).delete()
        Task.objects.filter(SAMPLEMD5=request.GET['md5']).delete()
        StaticAnalyzerAndroid.objects.filter(MD5=request.GET['md5']).delete()
        return samples(request)
    except:
        return HttpResponseRedirect('/not_found')


def get_tasks(reuqest):
    response_data = {}
    response_data['status'] = 'success'
    tasks = Task.objects.all()
    ts = []
    for i in tasks:
        temp = {}
        temp['id'] = i.id
        temp['name'] = i.NAME
        temp['member'] = i.MEMBER
        temp['sample'] = i.SAMPLEMD5
        temp['engines'] = i.ENGINES
        temp['progress'] = i.PROGRESS
        temp['TS'] = '{}-{}-{} {}:{}:{}'.format(i.TS.year, i.TS.month, i.TS.day, i.TS.hour, i.TS.minute, i.TS.second)
        temp['addr'] = '<a href="../report/?taskId=' + str(i.id) + '">查看</a>'
        ts.append(temp)
    response_data['tasks'] = ts
    return HttpResponse(json.dumps(response_data), content_type="application/json; charset=utf-8")


def upload_task(request):
    """
        Handle Task Upload
        """
    response_data = {}
    response_data['description'] = ''
    response_data['status'] = 'error'
    try:
        if request.method == 'POST':
            form = UploadTaskForm(request.POST)
            if form.is_valid():
                db_obj = Sample.objects.filter(MD5=request.POST['sample'])
                if db_obj.exists():
                    task = Task(
                        NAME=request.POST['name'], MEMBER=request.POST['member'], SAMPLEMD5=request.POST['sample'],
                        ENGINES=request.POST['engines'], PROGRESS=0, TS=timezone.now())
                    task.save()
                    dy_entry = ManualAnalyzerAndroid.objects.filter(MD5=task.SAMPLEMD5)
                    if not dy_entry.exists():
                        dynamic = ManualAnalyzerAndroid(MD5=request.POST['sample'])
                        dynamic.save()

                    engines = request.POST['engines'].split(",")
                    tasks.static_analysis.delay(task.id, task.SAMPLEMD5, engines)
                    response_data['status'] = 'success'
                    response_data['description'] = '任务添加成功'
                    print "\n[INFO] Adding Task"
            else:
                response_data['description'] = 'Invalid Form Data!'
                response_data['status'] = 'error'
                print "\n[ERROR] Invalid Form Data!"
        else:
            response_data['description'] = 'Method not Supported!'
            response_data['status'] = 'error'
            print "\n[ERROR] Method not Supported!"
    except:
        PrintException("[ERROR] Uploading File:")
    if response_data['status'] == 'error':
        resp = HttpResponse(json.dumps(
            response_data), content_type="application/json; charset=utf-8", status=500)
    else:
        resp = HttpResponse(json.dumps(response_data),
                            content_type="application/json; charset=utf-8")
    resp['Access-Control-Allow-Origin'] = '*'
    return resp


def deleteTask(request):
    taskid = request.GET['taskId']
    try:
        task = Task.objects.get(id=taskid)
        task.delete()
        return task_html(request)
    except:
        return HttpResponseRedirect('/not_found')


#  FUCK THE SHITTING ARCHITECTURE!!!!!!
def report(request):
    taskid = request.GET['taskId']
    try:
        task = Task.objects.get(id=taskid)
        db_entry = StaticAnalyzerAndroid.objects.filter(MD5=task.SAMPLEMD5)
        dy_entry = ManualAnalyzerAndroid.objects.filter(MD5=task.SAMPLEMD5)
        context = {}
        if db_entry.exists():
            context = get_context_from_db_entry(db_entry)
            context['finish'] = 1
            context['shell'] = 'false' if "Activity" in context['mainactivity'] else 'true'
            context['engines'] = task.ENGINES.split(",")
            engines = task.ENGINES.split(",")
            context['html'] = ""
            context['modal'] = ""
            context['js'] = ""
            context['md5'] = task.SAMPLEMD5
            for engine in engines:
                if engine == '0':
                    continue
                html, modal, js = generate_dynamic_html(engine, dy_entry[0])
                context['html'] += html
                context['modal'] += modal
                context['js'] += js

        else:
            context['finish'] = 0
            context['consoles'] = task.CONSOLES
        context['task_name'] = task.NAME
        context['task_id'] = task.id
        template = "static_analysis/report.html"
        return render(request, template, context)
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('/not_found')


def getTaskInfo(request):
    response_data = {}
    taskid = request.GET['taskId']
    try:
        task = Task.objects.get(id=taskid)
        db_entry = StaticAnalyzerAndroid.objects.filter(MD5=task.SAMPLEMD5)
        if db_entry.exists():
            response_data['finish'] = 1
        else:
            response_data['finish'] = 0
            response_data['consoles'] = task.CONSOLES
        response_data['task_name'] = task.NAME
        response_data['task_id'] = task.id
        response_data['status'] = 'success'
        return HttpResponse(json.dumps(response_data), content_type="application/json; charset=utf-8")
    except:
        response_data['status'] = 'error'
        return HttpResponse(json.dumps({}), content_type="application/json; charset=utf-8")



def upload(request, api=False):
    """
    Handle File Upload based on App type
    """
    try:
        response_data = {}
        response_data['url'] = ''
        response_data['description'] = ''
        response_data['status'] = 'error'
        api_response = {}
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                file_type = request.FILES['file'].content_type
                print "[INFO] MIME Type: " + file_type + " FILE: " + request.FILES['file'].name
                if ((file_type in settings.APK_MIME) and
                        request.FILES['file'].name.lower().endswith('.apk')):
                        # APK
                    md5 = handle_uploaded_file(request.FILES['file'], '.apk')
                    if api:
                        api_response["hash"] = md5
                        api_response["scan_type"] = "apk"
                        api_response["file_name"] = request.FILES['file'].name
                    response_data['url'] = ('StaticAnalyzer/?name=' + request.FILES['file'].name +
                                            '&type=apk&checksum=' + md5)
                    response_data['status'] = 'success'
                    add_to_recent_scan(
                        request.FILES['file'].name, md5, response_data['url'])
                    print "\n[INFO] Performing Static Analysis of Android APK"
                elif ((file_type in settings.ZIP_MIME) and
                      request.FILES['file'].name.lower().endswith('.zip')):
                      # Android /iOS Zipped Source
                    md5 = handle_uploaded_file(request.FILES['file'], '.zip')
                    if api:
                        api_response["hash"] = md5
                        api_response["scan_type"] = "zip"
                        api_response["file_name"] = request.FILES['file'].name
                    response_data['url'] = ('StaticAnalyzer/?name=' + request.FILES['file'].name +
                                            '&type=zip&checksum=' + md5)
                    response_data['status'] = 'success'
                    add_to_recent_scan(
                        request.FILES['file'].name, md5, response_data['url'])
                    print "\n[INFO] Performing Static Analysis of Android/iOS Source Code"
                elif ((file_type in settings.IPA_MIME) and
                      request.FILES['file'].name.lower().endswith('.ipa')):
                      # iOS Binary
                    if platform.system() == "Darwin":  # Check for Mac OS X
                        md5 = handle_uploaded_file(
                            request.FILES['file'], '.ipa')
                        if api:
                            api_response["hash"] = md5
                            api_response["scan_type"] = "ipa"
                            api_response["file_name"] = request.FILES[
                                'file'].name
                        response_data['url'] = ('StaticAnalyzer_iOS/?name=' +
                                                request.FILES['file'].name +
                                                '&type=ipa&checksum=' + md5)
                        response_data['status'] = 'success'
                        add_to_recent_scan(
                            request.FILES['file'].name, md5, response_data['url'])
                        print "\n[INFO] Performing Static Analysis of iOS IPA"
                    else:
                        if api:
                            api_response[
                                "error"] = "Static Analysis of iOS IPA requires OSX"
                        response_data['url'] = 'mac_only/'
                        response_data['status'] = 'success'
                        print "\n[ERROR] Static Analysis of iOS IPA requires OSX"
                # Windows APPX
                elif (file_type in settings.APPX_MIME) and request.FILES['file'].name.lower().endswith('.appx'):
                    md5 = handle_uploaded_file(request.FILES['file'], '.appx')
                    if api:
                        api_response["hash"] = md5
                        api_response["scan_type"] = "appx"
                        api_response["file_name"] = request.FILES['file'].name
                    response_data['url'] = 'StaticAnalyzer_Windows/?name=' + \
                        request.FILES['file'].name + \
                        '&type=appx&checksum=' + md5
                    response_data['status'] = 'success'
                    add_to_recent_scan(
                        request.FILES['file'].name, md5, response_data['url'])
                    print "\n[INFO] Performing Static Analysis of Windows APP"
                else:
                    if api:
                        api_response["error"] = "File format not Supported!"
                    response_data['url'] = ''
                    response_data['description'] = 'File format not Supported!'
                    response_data['status'] = 'error'
                    print "\n[ERROR] File format not Supported!"

            else:
                if api:
                    api_response["error"] = "Invalid Form Data!"
                response_data['url'] = ''
                response_data['description'] = 'Invalid Form Data!'
                response_data['status'] = 'error'
                print "\n[ERROR] Invalid Form Data!"
        else:
            if api:
                api_response["error"] = "Method not Supported!"
            response_data['url'] = ''
            response_data['description'] = 'Method not Supported!'
            response_data['status'] = 'error'
            print "\n[ERROR] Method not Supported!"
            form = UploadFileForm()
    except:
        PrintException("[ERROR] Uploading File:")
    if api:
        return api_response
    else:
        if response_data['status'] == 'error':
            resp = HttpResponse(json.dumps(
                response_data), content_type="application/json; charset=utf-8", status=500)
        else:
            resp = HttpResponse(json.dumps(response_data),
                                content_type="application/json; charset=utf-8")
    resp['Access-Control-Allow-Origin'] = '*'
    return resp


def api_docs(request):
    """
    API Docs Route
    """
    context = {'title': 'REST API Docs', 'api_key': api_key()}
    template = "general/apidocs.html"
    return render(request, template, context)


def about(request):
    """
    About Route
    """
    context = {'title': 'About'}
    template = "general/about.html"
    return render(request, template, context)


def error(request):
    """
    Error Route
    """
    context = {'title': 'Error'}
    template = "general/error.html"
    return render(request, template, context)


def zip_format(request):
    """
    Zip Format Message Route
    """
    context = {'title': 'Zipped Source Instruction'}
    template = "general/zip.html"
    return render(request, template, context)


def mac_only(request):
    """
    Mac Ony Message Route
    """
    context = {'title': 'Supports OSX Only'}
    template = "general/ios.html"
    return render(request, template, context)


def not_found(request):
    """
    Not Found Route
    """
    context = {'title': 'Not Found'}
    template = "general/not_found.html"
    return render(request, template, context)


def recent_scans(request):
    """
    Show Recent Scans Route
    """
    db_obj = RecentScansDB.objects.all().order_by('-TS')
    context = {'title': 'Recent Scans', 'entries': db_obj}
    template = "general/recent.html"
    return render(request, template, context)


def search(request):
    """
    Search Scan by MD5 Route
    """
    md5 = request.GET['md5']
    if re.match('[0-9a-f]{32}', md5):
        db_obj = RecentScansDB.objects.filter(MD5=md5)
        if db_obj.exists():
            return HttpResponseRedirect('/' + db_obj[0].URL)
        else:
            return HttpResponseRedirect('/not_found')
    return HttpResponseRedirect('/error/')


def download(request):
    """
    Download from MobSF Route
    """

    def readFile(filename, chunk_size=8192):
        with open(filename, 'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    try:
        if request.method == 'GET':
            allowed_exts = settings.ALLOWED_EXTENSIONS
            filename = request.path.replace("/download/", "", 1)
            # Security Checks
            if "../" in filename:
                print "\n[ATTACK] Path Traversal Attack detected"
                return HttpResponseRedirect('/error/')
            ext = os.path.splitext(filename)[1]
            if ext in allowed_exts:
                dwd_file = os.path.join(settings.DWD_DIR, filename)
                if os.path.isfile(dwd_file):
                    # wrapper = FileWrapper(file(dwd_file))
                    # response = HttpResponse(
                    #     wrapper, content_type=allowed_exts[ext])
                    # response['Content-Length'] = os.path.getsize(dwd_file)
                    # return response
                    response = StreamingHttpResponse(readFile(dwd_file))
                    response['Content-Type'] = 'application/octet-stream'
                    response['Content-Length'] = os.path.getsize(dwd_file)
                    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)
                    return response
    except:
        PrintException("Error Downloading File")
    return HttpResponseRedirect('/error/')


def delete_scan(request, api=False):
    """
    Delete Scan from DB and remove the scan related files
    """
    try:
        if request.method == 'POST':
            if api:
                md5_hash = request.POST['hash']
            else:
                md5_hash = request.POST['md5']
            data = {'deleted': 'no'}
            if re.match('[0-9a-f]{32}', md5_hash):
                # Delete DB Entries
                scan = RecentScansDB.objects.filter(MD5=md5_hash)
                if scan.exists():
                    RecentScansDB.objects.filter(MD5=md5_hash).delete()
                    ScopeURLSandTests.objects.filter(MD5=md5_hash).delete()
                    StaticAnalyzerAndroid.objects.filter(MD5=md5_hash).delete()
                    StaticAnalyzerIPA.objects.filter(MD5=md5_hash).delete()
                    StaticAnalyzerIOSZIP.objects.filter(MD5=md5_hash).delete()
                    StaticAnalyzerWindows.objects.filter(MD5=md5_hash).delete()
                    # Delete Upload Dir Contents
                    app_upload_dir = os.path.join(settings.UPLD_DIR, md5_hash)
                    if isDirExists(app_upload_dir):
                        shutil.rmtree(app_upload_dir)
                    # Delete Download Dir Contents
                    dw_dir = settings.DWD_DIR
                    for item in os.listdir(dw_dir):
                        item_path = os.path.join(dw_dir, item)
                        # Delete all related files
                        if isFileExists(item_path) and item.startswith(md5_hash + "-"):
                            os.remove(item_path)
                        # Delete related directories
                        if isDirExists(item_path) and item.startswith(md5_hash + "-"):
                            shutil.rmtree(item_path)
                    data = {'deleted': 'yes'}
            if api:
                return data
            else:
                return HttpResponse(json.dumps(data), content_type='application/json; charset=utf-8')
    except Exception as exp:
        msg = str(exp)
        exp_doc = exp.__doc__
        if api:
            return print_n_send_error_response(request, msg, True, exp_doc)
        else:
            return print_n_send_error_response(request, msg, False, exp_doc)
