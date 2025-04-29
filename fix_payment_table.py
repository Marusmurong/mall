import psycopg2

# 连接到数据库
conn = psycopg2.connect(
    dbname="cartit_mall",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

# 创建游标
cursor = conn.cursor()

try:
    # 检查字段是否存在
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='payment_payment' AND column_name='transaction_id';
    """)
    
    if cursor.fetchone() is None:
        print("添加 transaction_id 字段...")
        # 添加缺少的字段
        cursor.execute("""
            ALTER TABLE payment_payment
            ADD COLUMN transaction_id VARCHAR(255) NULL;
        """)
        conn.commit()
        print("字段添加成功!")
    else:
        print("transaction_id 字段已存在")
        
except Exception as e:
    print(f"发生错误: {e}")
    conn.rollback()
finally:
    # 关闭游标和连接
    cursor.close()
    conn.close() 