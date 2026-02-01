# 基金盯盘 PWA

零成本、去 AI 化的移动端基金盯盘工具，基于 Vercel Serverless Functions 部署。

## 功能特性

### 核心功能
- **我的持仓** - 添加/删除持仓基金，实时计算当日收益
- **自选基金** - 关注基金估值，查看连涨/跌天数和30天趋势
- **市场行情** - 全球指数实时行情，成交量趋势
- **板块行情** - 行业板块涨跌幅和主力资金流向
- **板块基金** - 按行业板块查询相关基金列表

### 技术特点
- **PWA 支持** - 可安装到手机主屏幕，离线访问
- **LocalStorage 持久化** - 数据存储在本地，无需登录
- **无状态 API** - 后端仅作为代理，解决 CORS 跨域问题
- **移动端优先** - 深色主题，底部导航，卡片式布局

## 项目结构

```
fund-pwa/
├── api/                    # Vercel Serverless Functions
│   ├── fund.py            # 基金搜索/估值 API
│   ├── market.py          # 市场指数/成交量 API
│   └── sector.py          # 板块行情/基金 API
├── public/                 # 静态资源
│   ├── index.html         # PWA 主页面
│   ├── manifest.json      # PWA 配置
│   ├── sw.js              # Service Worker
│   └── icons/             # PWA 图标
├── vercel.json            # Vercel 配置
├── requirements.txt       # Python 依赖
├── dev_server.py          # 本地开发服务器
└── test_api.py            # API 测试脚本
```

## 本地开发

### 启动开发服务器

```bash
cd fund-pwa
python3 dev_server.py
```

访问 http://localhost:3000

### 运行 API 测试

```bash
python3 test_api.py
```

## 部署到 Vercel

### 方式一：通过 Vercel CLI

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录并部署
vercel login
vercel --prod
```

### 方式二：通过 GitHub

1. 将代码推送到 GitHub 仓库
2. 在 Vercel Dashboard 中导入项目
3. 自动部署

## API 接口文档

### 基金 API (`/api/fund`)

| 参数 | 说明 |
|------|------|
| `action=search&code=000217` | 搜索基金 |
| `action=valuation&code=000217&fund_key=xxx` | 获取单只基金估值 |
| `action=batch_valuation&funds=code1:key1,code2:key2` | 批量获取估值 |

### 市场 API (`/api/market`)

| 参数 | 说明 |
|------|------|
| `action=indices` | 获取全球指数 |
| `action=volume&days=7` | 获取成交量趋势 |
| `action=intraday&count=20` | 获取上证分时数据 |

### 板块 API (`/api/sector`)

| 参数 | 说明 |
|------|------|
| `action=performance` | 获取板块涨跌排行 |
| `action=list` | 获取板块分类列表 |
| `action=funds&code=BK000217` | 获取板块基金列表 |

## 数据存储

应用使用浏览器 LocalStorage 存储数据：

- `holdings` - 持仓基金列表
- `watchlist` - 自选基金列表

数据格式：
```javascript
// holdings
{
  "000217": {
    "code": "000217",
    "name": "华安黄金ETF联接C",
    "fund_key": "xxx",
    "amount": 10000
  }
}

// watchlist
{
  "000217": {
    "code": "000217",
    "name": "华安黄金ETF联接C",
    "fund_key": "xxx"
  }
}
```

## 数据源

| 数据类型 | 数据源 |
|---------|--------|
| 基金搜索/估值 | fund123.cn |
| 全球指数 | 百度财经 |
| 成交量趋势 | 百度财经 |
| 板块行情 | 东方财富 |
| 板块基金 | 东方财富 |

## 注意事项

1. 本项目仅供学习和个人使用
2. 数据来自第三方，仅供参考，不构成投资建议
3. 部署到 Vercel 时需注意免费额度限制

## License

MIT
