# messaging/forms.py
from django import forms

class SendMessageForm(forms.Form):
    receiver_id = forms.IntegerField(label="ID receptor")
    subject = forms.CharField(max_length=255, required=False)
    content = forms.CharField(widget=forms.Textarea, max_length=5000)