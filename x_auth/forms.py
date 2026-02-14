from django import forms
from .models import ScheduledTweet

class TweetForm(forms.ModelForm):
    class Meta:
        model = ScheduledTweet
        fields = ['content', 'scheduled_time']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'ماذا تريد أن تنشر؟'}),
            'scheduled_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
        labels = {
            'content': 'محتوى التغريدة',
            'scheduled_time': 'وقت النشر المتوقع',
        }