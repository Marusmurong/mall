import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from payment.models import PaymentMethod

class Command(BaseCommand):
    help = '初始化基本支付方式'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新创建已存在的支付方式',
        )

    def handle(self, *args, **options):
        force = options['force']
        self.stdout.write('开始初始化支付方式...')
        
        payment_methods = [
            {
                'name': 'USDT (TRC20)',
                'code': 'usdt_trc20',
                'payment_type': 'usdt',
                'description': '使用USDT (TRC20网络) 支付，快速且安全。',
            },
            {
                'name': 'PayPal',
                'code': 'paypal',
                'payment_type': 'paypal',
                'description': '使用PayPal支付，安全便捷的全球支付解决方案。',
            },
            {
                'name': '信用卡/借记卡',
                'code': 'credit_card',
                'payment_type': 'credit_card',
                'description': '使用Visa、MasterCard、UnionPay等信用卡或借记卡安全支付。',
            }
        ]
        
        # 创建payment/management/commands/icons目录
        icons_dir = os.path.join(os.path.dirname(__file__), 'icons')
        os.makedirs(icons_dir, exist_ok=True)
        
        created_count = 0
        updated_count = 0
        
        for method_data in payment_methods:
            code = method_data['code']
            name = method_data['name']
            
            # 检查支付方式是否已存在
            payment_method, created = PaymentMethod.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'payment_type': method_data['payment_type'],
                    'description': method_data.get('description', ''),
                    'is_active': True,
                }
            )
            
            # 如果存在且force为True，则更新
            if not created and force:
                payment_method.name = name
                payment_method.payment_type = method_data['payment_type']
                payment_method.description = method_data.get('description', '')
                payment_method.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'更新支付方式: {name}'))
            elif created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'创建支付方式: {name}'))
            else:
                self.stdout.write(f'支付方式已存在，跳过: {name}')
        
        self.stdout.write('-' * 50)
        self.stdout.write(f'创建了 {created_count} 个新支付方式')
        self.stdout.write(f'更新了 {updated_count} 个已存在的支付方式')
        self.stdout.write(self.style.SUCCESS('支付方式初始化完成!')) 