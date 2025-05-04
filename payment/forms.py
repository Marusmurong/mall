from django import forms
from django.utils.translation import gettext_lazy as _
from .models import PaymentMethod

class PaymentMethodConfigForm(forms.ModelForm):
    """支付方式配置表单"""
    PAYMENT_TYPES = [
        ('usdt', 'USDT'),
        ('paypal', 'PayPal'),
        ('credit_card', '信用卡'),
        ('coinbase_commerce', 'Coinbase Commerce'),
    ]
    
    payment_type = forms.ChoiceField(choices=PAYMENT_TYPES, label='支付类型')
    
    # USDT配置字段
    usdt_wallet_address = forms.CharField(max_length=255, required=False, label='USDT钱包地址')
    usdt_api_key = forms.CharField(max_length=255, required=False, label='USDT API密钥')
    usdt_api_secret = forms.CharField(max_length=255, required=False, label='USDT API密钥')
    
    # PayPal配置字段
    paypal_client_id = forms.CharField(max_length=255, required=False, label='PayPal Client ID')
    paypal_client_secret = forms.CharField(max_length=255, required=False, widget=forms.PasswordInput(), label='PayPal Client Secret')
    paypal_mode = forms.ChoiceField(choices=[('sandbox', '沙盒模式'), ('live', '正式环境')], required=False, label='PayPal环境')
    
    # 信用卡配置字段
    cc_provider = forms.ChoiceField(choices=[('stripe', 'Stripe'), ('other', '其他')], required=False, label='信用卡处理商')
    cc_api_key = forms.CharField(max_length=255, required=False, label='API密钥')
    cc_api_secret = forms.CharField(max_length=255, required=False, widget=forms.PasswordInput(), label='API密钥')
    
    # Coinbase Commerce配置字段
    coinbase_api_key = forms.CharField(max_length=255, required=False, label='Coinbase API Key')
    coinbase_webhook_secret = forms.CharField(max_length=255, required=False, widget=forms.PasswordInput(), label='Webhook Secret')
    coinbase_checkout_style = forms.ChoiceField(choices=[('hosted', '托管页面'), ('embedded', '嵌入式结账')], required=False, label='结账样式')
    
    class Meta:
        model = PaymentMethod
        fields = ['name', 'code', 'payment_type', 'description', 'icon', 'is_active', 'test_mode']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        
        if instance:
            # 设置已有实例的初始值
            config = instance.config or {}
            
            # USDT配置
            self.fields['usdt_wallet_address'].initial = config.get('wallet_address', '')
            self.fields['usdt_api_key'].initial = config.get('api_key', '')
            self.fields['usdt_api_secret'].initial = config.get('api_secret', '')
            
            # PayPal配置
            self.fields['paypal_client_id'].initial = config.get('client_id', '')
            self.fields['paypal_client_secret'].initial = config.get('client_secret', '')
            self.fields['paypal_mode'].initial = config.get('mode', 'sandbox')
            
            # 信用卡配置
            self.fields['cc_provider'].initial = config.get('provider', 'stripe')
            self.fields['cc_api_key'].initial = config.get('api_key', '')
            self.fields['cc_api_secret'].initial = config.get('api_secret', '')
            
            # Coinbase Commerce配置
            self.fields['coinbase_api_key'].initial = config.get('api_key', '')
            self.fields['coinbase_webhook_secret'].initial = config.get('webhook_secret', '')
            self.fields['coinbase_checkout_style'].initial = config.get('checkout_style', 'hosted')
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # 获取表单数据
        payment_type = self.cleaned_data.get('payment_type')
        
        # 初始化配置
        config = instance.config or {}
        
        # 根据支付类型设置配置
        if payment_type == 'usdt':
            config['wallet_address'] = self.cleaned_data.get('usdt_wallet_address', '')
            config['api_key'] = self.cleaned_data.get('usdt_api_key', '')
            config['api_secret'] = self.cleaned_data.get('usdt_api_secret', '')
        elif payment_type == 'paypal':
            config['client_id'] = self.cleaned_data.get('paypal_client_id', '')
            config['client_secret'] = self.cleaned_data.get('paypal_client_secret', '')
            config['mode'] = self.cleaned_data.get('paypal_mode', 'sandbox')
        elif payment_type == 'credit_card':
            config['provider'] = self.cleaned_data.get('cc_provider', 'stripe')
            config['api_key'] = self.cleaned_data.get('cc_api_key', '')
            config['api_secret'] = self.cleaned_data.get('cc_api_secret', '')
        elif payment_type == 'coinbase_commerce':
            config['api_key'] = self.cleaned_data.get('coinbase_api_key', '')
            config['webhook_secret'] = self.cleaned_data.get('coinbase_webhook_secret', '')
            config['checkout_style'] = self.cleaned_data.get('coinbase_checkout_style', 'hosted')
            
        # 更新配置
        instance.config = config
        
        if commit:
            instance.save()
            
        return instance 