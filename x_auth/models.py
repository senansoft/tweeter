from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class XToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.username}"


from django.db import models
from django.contrib.auth.models import User


# الجدول الجديد للمنشورات
# x_auth/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from difflib import SequenceMatcher

def calculate_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

class ScheduledTweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=280)
    scheduled_time = models.DateTimeField()
    is_posted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # شرط حماية: إذا لم يتم تعيين مستخدم بعد (لحظة إنشاء الكائن)، تخطى الفحص 
        # لأن الفحص سيحدث مرة أخرى فور استدعاء save() بعد تعيين المستخدم
        try:
            if not self.user:
                return
        except Exception:
            return

        # 1. التحقق من الحد الأقصى (24 منشور قيد الانتظار)
        pending_count = ScheduledTweet.objects.filter(user=self.user, is_posted=False).count()
        # نتحقق فقط عند إضافة منشور جديد (ليس لديه pk)
        if not self.pk and pending_count >= 24:
            raise ValidationError("عذراً، يمكنك جدولة 24 منشوراً فقط كحد أقصى في قائمة الانتظار.")

        # 2. التحقق من تشابه المحتوى (70%)
        existing_tweets = ScheduledTweet.objects.filter(user=self.user)
        if self.pk: 
            existing_tweets = existing_tweets.exclude(pk=self.pk)
            
        for tweet in existing_tweets:
            similarity = calculate_similarity(self.content, tweet.content)
            if similarity >= 0.70:
                raise ValidationError(
                    f"هذا المنشور مشابه جداً لمنشور آخر لديك بنسبة {int(similarity*100)}%. "
                    "قوانين X تمنع تكرار المحتوى، يرجى تعديله."
                )

    def save(self, *args, **kwargs):
        self.full_clean() # استدعاء التحقق قبل الحفظ
        super().save(*args, **kwargs)


