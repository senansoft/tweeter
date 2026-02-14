import requests
from django.utils import timezone
from django.conf import settings
from .models import XToken, ScheduledTweet
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.db import close_old_connections

def refresh_x_token(token_obj):
    """تجديد التوكن تلقائياً"""
    url = "https://api.twitter.com/2/oauth2/token"
    data = {
        "refresh_token": token_obj.refresh_token,
        "grant_type": "refresh_token",
        "client_id": settings.X_CLIENT_ID,
    }
    auth = (settings.X_CLIENT_ID, settings.X_CLIENT_SECRET)
    try:
        response = requests.post(url, data=data, auth=auth)
        if response.status_code == 200:
            new_token = response.json()
            token_obj.access_token = new_token['access_token']
            token_obj.refresh_token = new_token.get('refresh_token', token_obj.refresh_token)
            token_obj.expires_at = timezone.now() + timezone.timedelta(seconds=new_token['expires_in'])
            token_obj.save()
            return True
    except Exception as e:
        print(f"⚠️ خطأ أثناء تجديد التوكن: {e}")
    return False

# x_auth/operator.py
import requests
from django.utils import timezone
from .models import ScheduledTweet, XToken
from django.db import close_old_connections

# متغير عالمي لتخزين وقت "فك الحظر"
COOLDOWN_UNTIL = None 

def check_and_post_scheduled_tweets():
    global COOLDOWN_UNTIL
    close_old_connections()
    
    # فحص إذا كنا في فترة التبريد
    if COOLDOWN_UNTIL and timezone.now() < COOLDOWN_UNTIL:
        print(f"⏳ نظام التبريد نشط.. سأحاول مجدداً بعد {COOLDOWN_UNTIL}")
        return

    try:
        now = timezone.now()
        
        # صمام الأمان (10 دقائق بين المنشورات)
        ten_minutes_ago = now - timezone.timedelta(minutes=10)
        if ScheduledTweet.objects.filter(is_posted=True, updated_at__gte=ten_minutes_ago).exists():
            return 

        tweet = ScheduledTweet.objects.filter(scheduled_time__lte=now, is_posted=False).order_by('scheduled_time').first()

        if tweet:
            # ... كود التوكن والإرسال ...
            res = requests.post(url, json=payload, headers=headers)
            
            if res.status_code == 201:
                tweet.is_posted = True
                tweet.save()
                COOLDOWN_UNTIL = None # إعادة ضبط التبريد عند النجاح
                print(f"✅ تم النشر!")
            
            elif res.status_code == 429:
                # تفعيل التبريد لمدة 20 دقيقة
                COOLDOWN_UNTIL = timezone.now() + timezone.timedelta(minutes=20)
                print("🚨 تم استلام خطأ 429. تفعيل نظام التبريد لـ 20 دقيقة.")
            
            else:
                print(f"❌ خطأ X: {res.status_code}")

    except Exception as e:
        print(f"⚠️ خطأ: {e}")
    finally:
        close_old_connections()
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # الفحص كل دقيقة (للدقة) ولكن المنطق الداخلي يضمن فاصل الـ 10 دقائق
    scheduler.add_job(
        check_and_post_scheduled_tweets, 
        'interval', 
        minutes=1, 
        name='check_tweets_job', 
        jobstore='default', 
        replace_existing=True
    )
    
    scheduler.start()
    print("🚀 المجدول الذكي يعمل (فحص كل دقيقة + حماية كل 10 دقائق).")