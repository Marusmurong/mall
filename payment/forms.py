from django import forms
from django.utils.translation import gettext_lazy as _
from .models import PaymentMethod

class PaymentMethodConfigForm(forms.ModelForm):
    # USDT配置字段
    usdt_wallet_address = forms.CharField(
        label=_('USDT钱包地址'), 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    usdt_api_key = forms.CharField(
        label=_('API密钥'), 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    usdt_api_secret = forms.CharField(
        label=_('API密钥Secret'), 
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    # PayPal配置字段
    paypal_client_id = forms.CharField(
        label=_('PayPal Client ID'), 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    paypal_client_secret = forms.CharField(
        label=_('PayPal Client Secret'), 
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    paypal_mode = forms.ChoiceField(
        label=_('PayPal环境'), 
        required=False,
        choices=[('sandbox', 'Sandbox测试环境'), ('live', '生产环境')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # 信用卡配置字段
    cc_api_key = forms.CharField(
        label=_('信用卡API密钥'), 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cc_api_secret = forms.CharField(
        label=_('信用卡API密钥Secret'), 
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    cc_provider = forms.ChoiceField(
        label=_('信用卡支付提供商'), 
        required=False,
        choices=[('stripe', 'Stripe'), ('paypal', 'PayPal信用卡支付'), ('other', '其他')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Coinbase商务配置字段
    coinbase_api_key = forms.CharField(
        label=_('Coinbase API密钥'), 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    coinbase_webhook_secret = forms.CharField(
        label=_('Webhook密钥'), 
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    coinbase_checkout_style = forms.ChoiceField(
        label=_('结账页面样式'), 
        required=False,
        choices=[('hosted', '托管页面'), ('inline', '内嵌页面')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = PaymentMethod
        fields = ['name', 'code', 'payment_type', 'description', 'icon', 'is_active', 'test_mode']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        
        if instance:
            # 预填充配置字段
            if instance.payment_type == 'usdt':
                self.fields['usdt_wallet_address'].initial = instance.get_config('wallet_address', '')
                self.fields['usdt_api_key'].initial = instance.get_config('api_key', '')
                self.fields['usdt_api_secret'].initial = instance.get_config('api_secret', '')
            
            elif instance.payment_type == 'paypal':
                self.fields['paypal_client_id'].initial = instance.get_config('client_id', '')
                self.fields['paypal_client_secret'].initial = instance.get_config('client_secret', '')
                self.fields['paypal_mode'].initial = instance.get_config('mode', 'sandbox')
            
            elif instance.payment_type == 'credit_card':
                self.fields['cc_api_key'].initial = instance.get_config('api_key', '')
                self.fields['cc_api_secret'].initial = instance.get_config('api_secret', '')
                self.fields['cc_provider'].initial = instance.get_config('provider', 'stripe')
                
            elif instance.payment_type == 'coinbase_commerce':
                self.fields['coinbase_api_key'].initial = instance.get_config('api_key', '')
                self.fields['coinbase_webhook_secret'].initial = instance.get_config('webhook_secret', '')
                self.fields['coinbase_checkout_style'].initial = instance.get_config('checkout_style', 'hosted')
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # 保存配置数据到JSON字段
        if instance.payment_type == 'usdt':
            instance.config = {
                'wallet_address': self.cleaned_data.get('usdt_wallet_address', ''),
                'api_key': self.cleaned_data.get('usdt_api_key', ''),
                'api_secret': self.cleaned_data.get('usdt_api_secret', '')
            }
        
        elif instance.payment_type == 'paypal':
            instance.config = {
                'client_id': self.cleaned_data.get('paypal_client_id', ''),
                'client_secret': self.cleaned_data.get('paypal_client_secret', ''),
                'mode': self.cleaned_data.get('paypal_mode', 'sandbox')
            }
        
        elif instance.payment_type == 'credit_card':
            instance.config = {
                'api_key': self.cleaned_data.get('cc_api_key', ''),
                'api_secret': self.cleaned_data.get('cc_api_secret', ''),
                'provider': self.cleaned_data.get('cc_provider', 'stripe')
            }
            
        elif instance.payment_type == 'coinbase_commerce':
            instance.config = {
                'api_key': self.cleaned_data.get('coinbase_api_key', ''),
                'webhook_secret': self.cleaned_data.get('coinbase_webhook_secret', ''),
                'checkout_style': self.cleaned_data.get('coinbase_checkout_style', 'hosted')
            }
        
        if commit:
            instance.save()
        
        return instance 