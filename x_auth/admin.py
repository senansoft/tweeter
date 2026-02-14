# Register your models here.
from django.contrib import admin
from .models import XToken, ScheduledTweet

admin.site.register(XToken)

@admin.register(ScheduledTweet)
class ScheduledTweetAdmin(admin.ModelAdmin):
    list_display = ('content', 'scheduled_time', 'is_posted', 'user')
    list_filter = ('is_posted', 'scheduled_time')
    ordering = ('scheduled_time',) 