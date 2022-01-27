import datetime
import json
import os
from ssl import AlertDescription

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
#from sympy import re
from .models import User
from django.utils import timezone
from .models import News, Recruit, User,Lecture
from .models import News, User, UploadFile, Diary
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from config import settings

###########
# Front   #
###########
# 1. HTML 파일 경로 지정 및 초기 세팅
@csrf_exempt
def login(request):
    if request.method == 'POST':
        
        user_id = request.POST.get("user_id")
        user_pw = request.POST.get("user_pw")

        # user = User.objects.get(user_id=user_id, user_pw=user_pw)
        try:
            # 데이터 조회를 성공했을 때
            user = User.objects.get(user_id=user_id, user_pw=user_pw)

            # 세션 만들기
            request.session["user_id"] = user.user_id
            request.session["user_name"] = user.user_name

        except Exception as e:
            print(e)
            return JsonResponse({'code': 500})
            
        return JsonResponse({'code': 200})
    else:
        return render(request, 'diaryapp/login.html')


def main(request):
    # 메인 페이지 초기 데이터 보내기.
    news=News.objects.order_by('?')
    p1 = Paginator(news,4)
    news_main = p1.page(1)
    lecture_today=Lecture.objects.filter(date=datetime.datetime.today())
    lecture_back=Lecture.objects.filter(date=datetime.datetime.today()-datetime.timedelta(1))
    lecture_front=Lecture.objects.filter(date=datetime.datetime.today()+datetime.timedelta(1))

    recruit=Recruit.objects.order_by('-date')
    p3 = Paginator(recruit,3)
    recruit = p3.page(1)
    return render(request,
    'diaryapp/index.html',{'recruit':recruit,'lecture':lecture_today,
    'lecture_f':lecture_front,'lecture_b':lecture_back,'news':news_main})
    

def diary(request):
    lec1 = Lecture.objects.filter(professor_id=0)  #diary sidebar 부분
    lec2 = Lecture.objects.filter(professor_id=1)
    lec3 = Lecture.objects.filter(professor_id=2)
    lec4 = Lecture.objects.filter(professor_id=5)
    return render(request, 'diaryapp/diary.html', 
        {'lec1':lec1, 'lec2':lec2,'lec3':lec3,'lec4':lec4})
  


def lecture(request):
    lecture_list = Lecture.objects.all()

    page = request.GET.get('page','1')
    p = Paginator(lecture_list,'7')
    lecture_data = p.page(page)
    return render(request, 'diaryapp/lecture.html', {'date' : lecture_data})

def news(request):
    news_list = News.objects.all()
    page=request.GET.get('page','1')
    p = Paginator(news_list,'5')
    news_data = p.page(page)
    return render(request, 'diaryapp/news.html', {'news_data' : news_data})


def hire(request):
    recruit_list=Recruit.objects.filter(date=datetime.datetime.today())[:48]
    page=request.GET.get('page','1')
    p=Paginator(recruit_list,'4')
    recruit=p.page(page)
    return render(request,
    'diaryapp/hire.html',{'recruit':recruit})


def team(request):
    return render(request, 'diaryapp/team.html')


def temp(request):
    return render(request, 'diaryapp/temp.html')


###########
# Back   #
###########
# API 코드
# 2. 이벤트 

# 2. 1. 로그인
#   위 Front쪽 추가 됨


# 2. 2. 회원가입
def signup_user(request):
    if request.method == 'POST':
        req = json.loads(request.body.decode('utf-8'))
        user_id = req["user_id"]#request.POST.get('user_id')
        user_pw = req["user_pw"]#request.POST.get('user_pw')
        user_name = req["user_name"]#request.POST.get('user_name')
        
        print(user_id, user_pw, user_name)

        # TODO 기존 사용자 동일한 id 있는지?
        # TODO 이메일 정규식 추가
        try:
            m = User(
                user_id = user_id,
                user_pw = user_pw, 
                user_name = user_name
            )
            m.date = timezone.now()
            m.save()
        except Exception as e:
            print("Error : ", e)
            pass
    
        data = {
                "isLogined": True,
                "user_name" : user_name
                }
        # return render(request, 'diaryapp/login.html', data)
        return JsonResponse(data=data)
    else:
        return render(request, 'diaryapp/login.html')

@csrf_exempt
def is_existed_user(request):
    if request.method == 'POST':
        req = json.loads(request.body.decode('utf-8'))
        user_id = req["user_id"]
        
        try:
            data = User.objects.filter(user_id=user_id)
            rep = list(data.values())
            
        except Exception as e:
            print("Error : ", e)
        
        if len(rep) > 0:
            data = {"result": True}
            return JsonResponse(data=data)
        else:
            data = {"result": False}
            return JsonResponse(data=data)

def check_session(request):
    if "user_id" not in request.session:
        return JsonResponse({'code': 500})
    return JsonResponse({'code': 200})

# 2. 3. 로그아웃
def logout(request):
    try:
        del request.session["user_id"]
        del request.session["user_name"]
    except KeyError:
        return redirect("diaryapp:login")    

    return redirect("diaryapp:login")

# 2. 4. 뉴스 
#    1) 뉴스 모든 데이터 조회
def read_all_news(request):
    data = News.objects.all()
    data=list(data.values())
    return JsonResponse(data,safe=False)

# 2. 5. 채용정보 
# 2. 5. 1. 채용 모든 데이터 조회
def read_all_recruit(request):
    data = Recruit.objects.all()
    data=list(data.values())
    return JsonResponse(data,safe=False)


# 2. 6. 강의
# 2. 6. 1. 강의 모든 데이터 조회
def read_all_lecture(request):
    data = Lecture.objects.all()
    data=list(data.values())
    return JsonResponse(data,safe=False)


# 2. 7. TIL관련


# 3. 파일 업로드

app_name = 'diaryapp'

def upload(request):
    if request.method == 'POST':
        diary = Diary()
        diary.title = request.POST['title']
        diary.content = request.POST['content']
        diary.date = timezone.datetime.now()
        diary.user = request.user
        diary.save()
        for img in request.FILES.getlist('imgs'):
            uploadfile = UploadFile()
            # 외래키로 현재 생성한 Post의 기본키를 참조
            uploadfile.diary = diary
            # imgs로부터 가져온 파일 하나를 저장
            uploadfile.file = img
            # 데이터베이스에 저장
            uploadfile.save()
        return redirect('/diaryapp/fileview/' + str(diary.id))
    return render(
        request, 'diaryapp/upload.html')

def download(request):
    id = request.GET.get('id')
    uploadFile = UploadFile.objects.get(id=id)

    filepath = str(settings.BASE_DIR) + ('/media/%s' % uploadFile.file.name)
    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        response = HttpResponse(f, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

def test(request):
    pass