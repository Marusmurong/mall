// 模拟数据，用于在后端API未启动时展示UI
export const mockWishlists = [
  {
    id: '1',
    name: '我的生日心愿单',
    description: '这是我的生日心愿单，希望朋友们能帮我实现愿望',
    is_public: true,
    share_code: 'birthday2025',
    created_at: '2025-03-15T10:30:00Z',
    updated_at: '2025-04-10T08:15:00Z',
    owner_name: '张三',
    items: [
      {
        id: '101',
        title: 'Apple iPhone 15 Pro Max',
        description: '最新款苹果手机，256GB，深空黑色',
        price: 9999.00,
        original_price: 10999.00,
        currency: 'CNY',
        image: 'https://picsum.photos/seed/iphone15/400/400',
        product_id: 'p101',
        added_at: '2025-03-15T11:30:00Z',
        purchased: false,
        purchased_at: null,
        purchased_by: null
      },
      {
        id: '102',
        title: 'Sony WH-1000XM5 无线降噪耳机',
        description: '索尼最新旗舰降噪耳机，黑色',
        price: 2799.00,
        original_price: 3099.00,
        currency: 'CNY',
        image: 'https://picsum.photos/seed/sony/400/400',
        product_id: 'p102',
        added_at: '2025-03-16T09:45:00Z',
        purchased: true,
        purchased_at: '2025-04-01T14:20:00Z',
        purchased_by: '李四'
      },
      {
        id: '103',
        title: 'Nintendo Switch OLED',
        description: '任天堂Switch OLED版本，白色',
        price: 2299.00,
        original_price: null,
        currency: 'CNY',
        image: 'https://picsum.photos/seed/switch/400/400',
        product_id: 'p103',
        added_at: '2025-03-18T16:20:00Z',
        purchased: false,
        purchased_at: null,
        purchased_by: null
      }
    ]
  },
  {
    id: '2',
    name: '新家装修心愿单',
    description: '搬新家需要的家居用品清单',
    is_public: true,
    share_code: 'newhome2025',
    created_at: '2025-02-20T14:00:00Z',
    updated_at: '2025-04-05T11:30:00Z',
    owner_name: '张三',
    items: [
      {
        id: '201',
        title: 'IKEA BILLY 书柜',
        description: '宜家经典书柜，白色，80x28x202厘米',
        price: 599.00,
        original_price: null,
        currency: 'CNY',
        image: 'https://picsum.photos/seed/bookshelf/400/400',
        product_id: 'p201',
        added_at: '2025-02-21T10:15:00Z',
        purchased: true,
        purchased_at: '2025-03-10T09:30:00Z',
        purchased_by: '王五'
      },
      {
        id: '202',
        title: 'Dyson V12 Detect Slim 无线吸尘器',
        description: '戴森最新款激光吸尘器',
        price: 4290.00,
        original_price: 4590.00,
        currency: 'CNY',
        image: 'https://picsum.photos/seed/dyson/400/400',
        product_id: 'p202',
        added_at: '2025-02-22T16:40:00Z',
        purchased: false,
        purchased_at: null,
        purchased_by: null
      }
    ]
  },
  {
    id: '3',
    name: '旅行装备心愿单',
    description: '计划去欧洲旅行需要的装备',
    is_public: false,
    share_code: 'eurotrip2025',
    created_at: '2025-01-10T08:45:00Z',
    updated_at: '2025-03-20T15:10:00Z',
    owner_name: '张三',
    items: [
      {
        id: '301',
        title: 'Osprey Farpoint 40 旅行背包',
        description: '40升旅行背包，适合作为随身行李',
        price: 1199.00,
        original_price: 1399.00,
        currency: 'CNY',
        image: 'https://picsum.photos/seed/backpack/400/400',
        product_id: 'p301',
        added_at: '2025-01-11T09:20:00Z',
        purchased: false,
        purchased_at: null,
        purchased_by: null
      },
      {
        id: '302',
        title: 'Bose QuietComfort 耳塞',
        description: '降噪耳塞，适合长途飞行',
        price: 1999.00,
        original_price: null,
        currency: 'CNY',
        image: 'https://picsum.photos/seed/bose/400/400',
        product_id: 'p302',
        added_at: '2025-01-12T14:30:00Z',
        purchased: false,
        purchased_at: null,
        purchased_by: null
      },
      {
        id: '303',
        title: 'Anker 65W 充电器',
        description: '多口USB-C充电器，适合旅行使用',
        price: 299.00,
        original_price: 349.00,
        currency: 'CNY',
        image: 'https://picsum.photos/seed/anker/400/400',
        product_id: 'p303',
        added_at: '2025-01-15T11:45:00Z',
        purchased: true,
        purchased_at: '2025-02-05T16:20:00Z',
        purchased_by: '赵六'
      }
    ]
  }
];

export const mockSharedWishlist = {
  id: '1',
  name: '我的生日心愿单',
  description: '这是我的生日心愿单，希望朋友们能帮我实现愿望',
  is_public: true,
  share_code: 'birthday2025',
  created_at: '2025-03-15T10:30:00Z',
  updated_at: '2025-04-10T08:15:00Z',
  owner_name: '张三',
  items: [
    {
      id: '101',
      title: 'Apple iPhone 15 Pro Max',
      description: '最新款苹果手机，256GB，深空黑色',
      price: 9999.00,
      original_price: 10999.00,
      currency: 'CNY',
      image: 'https://picsum.photos/seed/iphone15/400/400',
      product_id: 'p101',
      added_at: '2025-03-15T11:30:00Z',
      purchased: false,
      purchased_at: null,
      purchased_by: null
    },
    {
      id: '102',
      title: 'Sony WH-1000XM5 无线降噪耳机',
      description: '索尼最新旗舰降噪耳机，黑色',
      price: 2799.00,
      original_price: 3099.00,
      currency: 'CNY',
      image: 'https://picsum.photos/seed/sony/400/400',
      product_id: 'p102',
      added_at: '2025-03-16T09:45:00Z',
      purchased: true,
      purchased_at: '2025-04-01T14:20:00Z',
      purchased_by: '李四'
    },
    {
      id: '103',
      title: 'Nintendo Switch OLED',
      description: '任天堂Switch OLED版本，白色',
      price: 2299.00,
      original_price: null,
      currency: 'CNY',
      image: 'https://picsum.photos/seed/switch/400/400',
      product_id: 'p103',
      added_at: '2025-03-18T16:20:00Z',
      purchased: false,
      purchased_at: null,
      purchased_by: null
    }
  ]
};
