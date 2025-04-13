from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='必填。请输入有效的电子邮件地址。')
    invite_code = forms.CharField(max_length=12, required=True, help_text='必填。请输入邀请码。')
    phone = forms.CharField(max_length=20, required=False, help_text='选填。请输入您的手机号码。')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'invite_code', 'phone')
    
    def clean_invite_code(self):
        invite_code = self.cleaned_data.get('invite_code')
        if not UserProfile.objects.filter(invite_code=invite_code).exists():
            raise forms.ValidationError('邀请码无效，请检查后重新输入。')
        return invite_code
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # 获取邀请人
            invite_code = self.cleaned_data['invite_code']
            inviter_profile = UserProfile.objects.get(invite_code=invite_code)
            
            # 更新用户资料
            user.profile.inviter = inviter_profile
            user.profile.phone = self.cleaned_data.get('phone', '')
            user.profile.save()
            
            # 创建邀请记录
            from .models import InvitationRecord
            InvitationRecord.objects.create(
                inviter=inviter_profile,
                invitee=user.profile,
                invite_code=invite_code,
                status='accepted'
            )
        
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone', 'avatar', 'bio')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False 