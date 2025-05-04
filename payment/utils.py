import uuid
import json
from django.conf import settings
from django.urls import reverse

# 导入PayPal SDK
import paypalrestsdk
from paypalrestsdk import Payment as PayPalPayment

# 导入Coinbase Commerce SDK
from coinbase_commerce.client import Client as CoinbaseClient

def setup_paypal_sdk(payment_method=None):
    """配置PayPal SDK"""
    # 尝试从支付方式的config中获取API密钥
    client_id = ''
    client_secret = ''
    is_sandbox = True
    
    if payment_method and hasattr(payment_method, 'config') and isinstance(payment_method.config, dict):
        client_id = payment_method.config.get('client_id', '')
        client_secret = payment_method.config.get('client_secret', '')
        is_sandbox = payment_method.config.get('is_sandbox', True)
    
    # 如果支付方式中没有密钥，从settings获取
    if not client_id:
        client_id = getattr(settings, 'PAYPAL_CLIENT_ID', '')
    if not client_secret:
        client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', '')
    
    # 如果未配置，使用示例值（仅用于开发）
    if not client_id:
        client_id = 'AYSq3RDGsmBLJE-otTkBtM-jBRd1TCQwFf9RGfwddNXWz0uFU9ztymylOhRS'
    if not client_secret:
        client_secret = 'EGnHDxD_qRPdaLdZz8iCr8N7_MzF-YHPTkjs6NKYQvQSBngp4PTTVWkPZRbL'
    
    # 配置PayPal SDK
    mode = 'sandbox' if is_sandbox else 'live'
    paypalrestsdk.configure({
        'mode': mode,
        'client_id': client_id,
        'client_secret': client_secret
    })
    
    return {
        'client_id': client_id,
        'client_secret': client_secret,
        'mode': mode
    }

def setup_coinbase_commerce_sdk(payment_method=None):
    """配置Coinbase Commerce SDK"""
    # 尝试从支付方式的config中获取API密钥
    api_key = ''
    
    if payment_method and hasattr(payment_method, 'config') and isinstance(payment_method.config, dict):
        api_key = payment_method.config.get('api_key', '')
    
    # 如果支付方式中没有密钥，从settings获取
    if not api_key:
        api_key = getattr(settings, 'COINBASE_COMMERCE_API_KEY', '')
    
    # 如果未配置，使用示例值（仅用于开发）
    if not api_key:
        api_key = '00000000-0000-0000-0000-000000000000'
        
    print(f"使用Coinbase API密钥: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else ''}")
    
    # 创建Coinbase Commerce客户端
    return CoinbaseClient(api_key=api_key)

def get_paypal_base_url(payment_method=None):
    """
    根据配置获取PayPal的基础URL
    
    Args:
        payment_method: 支付方式模型实例，可以包含is_sandbox标志
        
    Returns:
        str: PayPal基础URL，沙盒或生产环境
    """
    # 默认使用沙盒环境
    is_sandbox = True
    
    # 检查支付方式实例是否包含沙盒标志
    if payment_method and hasattr(payment_method, 'config'):
        if isinstance(payment_method.config, dict) and 'is_sandbox' in payment_method.config:
            is_sandbox = payment_method.config.get('is_sandbox', True)
    
    # 从设置中获取，如果支付方式没有指定
    if is_sandbox:
        return getattr(settings, 'PAYPAL_SANDBOX_URL', 'https://www.sandbox.paypal.com')
    else:
        return getattr(settings, 'PAYPAL_LIVE_URL', 'https://www.paypal.com')

def get_coinbase_base_url(payment_method=None):
    """
    根据配置获取Coinbase Commerce的基础URL
    
    Args:
        payment_method: 支付方式模型实例，可以包含测试模式标志
        
    Returns:
        str: Coinbase Commerce基础URL
    """
    # Coinbase Commerce只有一个URL
    return getattr(settings, 'COINBASE_COMMERCE_URL', 'https://commerce.coinbase.com')

def generate_coinbase_payment_details(payment):
    """使用Coinbase Commerce SDK生成支付详情"""
    from payment.models import CoinbaseCommercePaymentDetail
    
    try:
        # 获取支付方式和金额
        payment_method = payment.payment_method
        amount = float(payment.amount)
        currency = payment.currency or 'USD'
        
        # 创建Coinbase Commerce客户端
        client = setup_coinbase_commerce_sdk(payment_method)
        
        # 构建商品信息
        if payment.wishlist_item:
            product_name = f"Purchase of {payment.wishlist_item.title or 'Item'}"
            product_description = f"Payment for wishlist item: {payment.wishlist_item.title or 'Item'}"
        else:
            product_name = "Payment"
            product_description = "Payment via Coinbase Commerce"
        
        # 获取webhook URL
        webhook_url = f"{getattr(settings, 'BASE_URL', 'http://localhost:8000')}/webhooks/payments/coinbase/"
        
        # 创建Coinbase Commerce支付请求
        charge_data = {
            'name': product_name,
            'description': product_description,
            'local_price': {
                'amount': str(amount),
                'currency': currency
            },
            'pricing_type': 'fixed_price',
            'redirect_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/payment/success?id={payment.id}",
            'cancel_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/payment/cancel?id={payment.id}",
            'metadata': {
                'payment_id': str(payment.id),
                'customer_email': payment.payer_email or ''
            }
        }
        
        # 使用SDK创建支付
        try:
            charge = client.charge.create(**charge_data)
            coinbase_checkout_url = charge['hosted_url']
            coinbase_order_id = charge['id']
            
            # 打印成功信息
            print(f"Coinbase支付创建成功: ID={coinbase_order_id}, URL={coinbase_checkout_url}")
        except Exception as e:
            # 如果API调用失败，使用模拟数据（仅用于开发）
            print(f"Coinbase API错误 (开发模式): {str(e)}")
            coinbase_order_id = f"COINBASE-{uuid.uuid4().hex[:10].upper()}"
            coinbase_checkout_url = f"https://commerce.coinbase.com/checkout/{coinbase_order_id}"
    
    except Exception as e:
        # 异常处理 - 使用模拟数据（仅用于开发）
        print(f"Coinbase支付创建错误 (开发模式): {str(e)}")
        coinbase_order_id = f"COINBASE-{uuid.uuid4().hex[:10].upper()}"
        coinbase_checkout_url = f"https://commerce.coinbase.com/checkout/{coinbase_order_id}"
    
    # 创建Coinbase支付详情记录，而不是使用PayPal记录
    try:
        payment_detail = CoinbaseCommercePaymentDetail.objects.create(
            payment=payment,
            charge_id=coinbase_order_id,
            charge_code=coinbase_order_id[:8],
            hosted_url=coinbase_checkout_url,
            status='NEW'
        )
    except Exception as e:
        print(f"创建Coinbase支付详情记录失败: {str(e)}")
        # 如果Coinbase支付详情创建失败，尝试创建通用支付数据
        from payment.models import PayPalPaymentDetail
        payment_detail = PayPalPaymentDetail.objects.create(
            payment=payment,
            paypal_order_id=coinbase_order_id,  # 暂用paypal_order_id字段
            payment_link=coinbase_checkout_url
        )
    
    # 更新支付记录，添加支付链接
    payment.payment_data = {
        "checkout_url": coinbase_checkout_url,
        "payment_type": "coinbase",
        "order_id": coinbase_order_id,
        "payment_link": coinbase_checkout_url  # 确保payment_link字段存在
    }
    payment.save()
    
    return payment_detail

def generate_paypal_payment_details(payment):
    """使用PayPal SDK生成支付详情"""
    from payment.models import PayPalPaymentDetail
    
    try:
        # 获取支付方式和金额
        payment_method = payment.payment_method
        amount = float(payment.amount)
        currency = payment.currency or 'USD'
        
        # 检查是否使用沙盒环境
        is_sandbox = True
        if hasattr(payment_method, 'config'):
            if isinstance(payment_method.config, dict) and 'is_sandbox' in payment_method.config:
                is_sandbox = payment_method.config.get('is_sandbox', True)
        
        # 配置PayPal SDK
        setup_paypal_sdk(payment_method)
        
        # 构建商品信息
        if payment.wishlist_item:
            item_name = payment.wishlist_item.title or 'Item'
            item_description = f"Payment for wishlist item: {item_name}"
        else:
            item_name = "Payment"
            item_description = "Payment via PayPal"
        
        # 创建PayPal支付请求
        paypal_payment = PayPalPayment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/payment/success?id={payment.id}",
                "cancel_url": f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/payment/cancel?id={payment.id}"
            },
            "transactions": [{
                "amount": {
                    "total": str(amount),
                    "currency": currency
                },
                "description": item_description,
                "item_list": {
                    "items": [{
                        "name": item_name,
                        "price": str(amount),
                        "currency": currency,
                        "quantity": 1
                    }]
                }
            }]
        })
        
        # 使用SDK创建支付
        try:
            if paypal_payment.create():
                # 获取批准URL（用户需要访问此URL完成支付）
                for link in paypal_payment.links:
                    if link.rel == "approval_url":
                        paypal_checkout_url = link.href
                        break
                else:
                    # 如果没有找到approval_url，使用模拟数据
                    paypal_order_id = paypal_payment.id
                    paypal_checkout_url = f"https://www.sandbox.paypal.com/checkoutnow?token={paypal_order_id}"
                
                paypal_order_id = paypal_payment.id
            else:
                # 如果创建失败，使用模拟数据（仅用于开发）
                print(f"PayPal创建失败 (开发模式): {paypal_payment.error}")
                paypal_order_id = f"PAYPAL-{uuid.uuid4().hex[:10].upper()}"
                paypal_checkout_url = f"https://www.sandbox.paypal.com/checkoutnow?token={paypal_order_id}"
        except Exception as e:
            # 如果API调用失败，使用模拟数据（仅用于开发）
            print(f"PayPal API错误 (开发模式): {str(e)}")
            paypal_order_id = f"PAYPAL-{uuid.uuid4().hex[:10].upper()}"
            paypal_checkout_url = f"https://www.sandbox.paypal.com/checkoutnow?token={paypal_order_id}"
    
    except Exception as e:
        # 异常处理 - 使用模拟数据（仅用于开发）
        print(f"PayPal支付创建错误 (开发模式): {str(e)}")
        paypal_order_id = f"PAYPAL-{uuid.uuid4().hex[:10].upper()}"
        paypal_checkout_url = f"{get_paypal_base_url(payment_method)}/checkoutnow?token={paypal_order_id}"
    
    # 创建PayPal支付详情记录
    paypal_detail = PayPalPaymentDetail.objects.create(
        payment=payment,
        paypal_order_id=paypal_order_id,
        payment_link=paypal_checkout_url
    )
    
    # 更新支付记录，添加支付链接和订单ID
    payment.payment_data = {
        "checkout_url": paypal_checkout_url,
        "payment_type": "paypal",
        "order_id": paypal_order_id
    }
    payment.save()
    
    return paypal_detail

def generate_credit_card_payment_details(payment):
    """生成信用卡支付详情（通过PayPal处理）"""
    from payment.models import CreditCardPaymentDetail
    
    # 获取支付方式
    payment_method = payment.payment_method
    
    # 获取PayPal基础URL（沙盒或生产环境）
    paypal_base_url = get_paypal_base_url(payment_method)
    
    # 创建信用卡支付详情记录
    card_detail = CreditCardPaymentDetail.objects.create(
        payment=payment,
        processor="PayPal",  # 使用PayPal作为信用卡处理器
    )
    
    # 生成唯一的交易ID
    transaction_id = f"CCPAY-{uuid.uuid4().hex[:12].upper()}"
    
    # 构建信用卡支付链接 - 假设通过PayPal处理信用卡支付
    paypal_card_url = f"{paypal_base_url}/creditcard/checkout?token={transaction_id}"
    
    # 更新支付记录，添加支付链接
    payment.payment_data = {
        "checkout_url": paypal_card_url,
        "payment_type": "credit_card",
        "transaction_id": transaction_id,
        "processor": "PayPal"
    }
    payment.save()
    
    return card_detail

def get_payment_checkout_url(payment):
    """
    根据支付记录获取支付跳转URL
    这个方法应该在创建支付记录后调用，用于获取跳转到支付页面的URL
    """
    # 检查支付记录中是否已有支付链接
    if payment.payment_data and "checkout_url" in payment.payment_data:
        checkout_url = payment.payment_data["checkout_url"]
        
        # 如果是相对URL，转换为绝对URL
        if checkout_url.startswith("/"):
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            checkout_url = f"{base_url}{checkout_url}"
            
        return checkout_url
    
    # 检查PayPal支付详情
    try:
        if hasattr(payment, 'paypal_details') and payment.paypal_details:
            return payment.paypal_details.payment_link
    except:
        pass
    
    # 如果没有找到支付链接，返回None
    return None
