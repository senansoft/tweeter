import os
import base64
import hashlib
import re
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from requests_oauthlib import OAuth2Session
from django.conf import settings
from django.contrib import messages  # الاستيراد الصحيح للرسائل
from django.core.exceptions import ValidationError  # استيراد ضروري لمعالجة أخطاء الموديل
from django.contrib.auth.decorators import login_required

from .models import XToken, ScheduledTweet
from .forms import TweetForm

# إعدادات OAuth2 و PKCE
client_id = settings.X_CLIENT_ID
redirect_uri = settings.X_REDIRECT_URI
scopes = ["tweet.read", "tweet.write", "users.read", "offline.access"]

# --- وظائف الربط مع X ---

def twitter_login(request):
    """الخطوة 1: توجيه المستخدم إلى X"""
    code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
    code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
    request.session['code_verifier'] = code_verifier
    
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8").replace("=", "")

    twitter = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
    authorization_url, state = twitter.authorization_url(
        "https://twitter.com/i/oauth2/authorize",
        code_challenge=code_challenge,
        code_challenge_method="S256",
    )
    
    request.session['oauth_state'] = state
    return redirect(authorization_url)

def twitter_callback(request):
    """الخطوة 2: استقبال الرد وحفظ التوكن"""
    code_verifier = request.session.get('code_verifier')
    state = request.session.get('oauth_state')
    
    twitter = OAuth2Session(client_id, redirect_uri=redirect_uri, state=state)
    
    try:
        token = twitter.fetch_token(
            token_url="https://api.twitter.com/2/oauth2/token",
            client_secret=settings.X_CLIENT_SECRET,
            authorization_response=request.build_absolute_uri(),
            code_verifier=code_verifier,
        )

        expires_in = token.get('expires_in', 7200)
        expires_at = timezone.now() + timedelta(seconds=expires_in)
        
        XToken.objects.update_or_create(
            user=request.user,
            defaults={
                'access_token': token.get('access_token'),
                'refresh_token': token.get('refresh_token'),
                'expires_at': expires_at,
            }
        )
        messages.success(request, "تم ربط حساب X بنجاح!")
        return redirect('dashboard')
    except Exception as e:
        return HttpResponse(f"حدث خطأ أثناء الربط: {str(e)}")

# --- وظائف لوحة التحكم (Dashboard) ---



@login_required
def dashboard(request):
    if request.method == 'POST':
        form = TweetForm(request.POST)
        if form.is_valid():
            try:
                new_tweet = form.save(commit=False)
                new_tweet.user = request.user
                # استدعاء full_clean يدوياً هنا يضمن تشغيل دالة clean() قبل الحفظ
                new_tweet.full_clean() 
                new_tweet.save()
                messages.success(request, "✅ تم جدولة المنشور بنجاح!")
                return redirect('dashboard')
            except ValidationError as e:
                # التقاط أخطاء التشابه والحد الأقصى وعرضها كرسائل للمستخدم
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors: messages.error(request, error)
                else:
                    messages.error(request, e.message)
        else:
            messages.error(request, "يرجى تصحيح الأخطاء في النموذج.")
    else:
        form = TweetForm()
    
    tweets = ScheduledTweet.objects.filter(user=request.user).order_by('-scheduled_time')
    return render(request, 'x_auth/dashboard.html', {'form': form, 'tweets': tweets})

@login_required
def delete_tweet(request, pk):
    tweet = get_object_or_404(ScheduledTweet, pk=pk, user=request.user)
    if not tweet.is_posted:
        tweet.delete()
        messages.success(request, "تم حذف المنشور بنجاح.")
    return redirect('dashboard')

@login_required
def edit_tweet(request, pk):
    tweet = get_object_or_404(ScheduledTweet, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TweetForm(request.POST, instance=tweet)
        if form.is_valid():
            try:
                updated_tweet = form.save(commit=False)
                updated_tweet.full_clean()
                updated_tweet.save()
                messages.success(request, "تم تحديث المنشور.")
                return redirect('dashboard')
            except ValidationError as e:
                messages.error(request, e.message)
    else:
        form = TweetForm(instance=tweet)
    return render(request, 'x_auth/edit_tweet.html', {'form': form})