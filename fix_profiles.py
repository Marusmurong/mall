import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

# 检查并为所有用户创建资料
for user in User.objects.all():
    try:
        profile = user.profile
        if not profile.invite_code:
            profile.save()  # 触发邀请码生成
            print(f"已为用户 {user.username} 生成邀请码: {profile.invite_code}")
        else:
            print(f"用户 {user.username} 已有邀请码: {profile.invite_code}")
    except:
        # 如果用户没有profile，创建一个
        profile = UserProfile.objects.create(user=user)
        print(f"已为用户 {user.username} 创建资料并生成邀请码: {profile.invite_code}")

print("\n所有用户现在都应该有邀请码了。请检查管理后台。") 