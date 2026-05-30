# 合租小程序

全网合租信息聚合 + AI 可信度评分的微信小程序。

## 功能特色

- 🔍 **全网聚合** - 豆瓣、58同城、闲鱼、小红书、微博等平台的合租信息一站式浏览
- 🤖 **AI 可信度评分** - 从价格合理性、评论区信号、发帖人信息、图片真实性、内容完整度 5 个维度智能评分
- 📱 **微信小程序** - 原生小程序开发，体验流畅
- 🔗 **一键跳转** - 点击即可查看原帖，复制链接方便分享

## 项目结构

```
合租小程序/
├── server/                      # Python 后端 (FastAPI)
│   ├── main.py                  # 入口
│   ├── config.py                # 配置
│   ├── database.py              # 数据库
│   ├── models/                  # 数据模型
│   ├── scrapers/                # 平台爬虫
│   │   ├── base.py              # 爬虫基类
│   │   ├── douban.py            # 豆瓣
│   │   └── fifty_eight.py       # 58同城
│   ├── services/                # 业务服务
│   │   ├── aggregator.py        # 聚合服务
│   │   └── credibility.py       # AI 评分
│   └── routers/                 # API 路由
├── miniprogram/                 # 微信小程序前端
│   ├── pages/
│   │   ├── index/               # 首页 - 帖子列表
│   │   ├── detail/              # 详情页 - AI评分展示
│   │   └── search/              # 搜索页
│   └── components/
│       ├── post-card/           # 帖子卡片
│       ├── credibility-badge/   # 可信度徽章
│       └── filter-bar/          # 筛选栏
└── README.md
```

## 快速开始

### 1. 后端启动

```bash
cd server

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入 AI API Key（可选，不填则使用规则引擎评分）

# 启动服务
python main.py
```

后端将在 http://localhost:8000 启动

### 2. 小程序开发

1. 用微信开发者工具打开 `miniprogram/` 目录
2. 修改 `app.js` 中的 `baseUrl` 为你的后端地址
3. 编译运行

### 3. API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/posts` | GET | 获取帖子列表（支持筛选） |
| `/api/posts/search` | GET | 搜索帖子 |
| `/api/posts/{id}` | GET | 获取帖子详情 |
| `/api/posts/sources` | GET | 获取支持的平台 |
| `/api/posts/refresh` | POST | 手动触发爬虫刷新 |
| `/health` | GET | 健康检查 |

#### 筛选参数

- `city` - 城市（默认：北京）
- `source` - 来源平台（douban/58/xianyu/xiaohongshu/weibo）
- `area` - 区域
- `min_price` / `max_price` - 价格区间
- `min_credibility` - 最低可信度评分
- `page` / `page_size` - 分页

## AI 可信度评分

| 维度 | 权重 | 说明 |
|------|------|------|
| 价格合理性 | 25% | 对比同区域市场价 |
| 评论区信号 | 25% | 负面关键词检测 |
| 发帖人信息 | 20% | 描述专业度、关键词 |
| 图片真实性 | 15% | 是否有实拍图 |
| 内容完整度 | 15% | 信息是否齐全 |

评分等级：
- 80-100：高度可信 ✅
- 60-79：较为可信 🟡
- 40-59：需谨慎 🟠
- 0-39：风险较高 🔴

## 添加新平台爬虫

1. 在 `server/scrapers/` 下新建文件，继承 `BaseScraper`
2. 实现 `scrape()` 方法
3. 在 `services/aggregator.py` 中注册

```python
from scrapers.base import BaseScraper, ScrapedPost

class NewPlatformScraper(BaseScraper):
    source_name = "new_platform"

    async def scrape(self, city="北京", keyword="合租") -> list[ScrapedPost]:
        # 实现爬取逻辑
        ...
```

## 技术栈

- **前端**：微信小程序原生开发
- **后端**：Python FastAPI
- **数据库**：SQLite（MVP）→ PostgreSQL（生产）
- **AI**：DeepSeek / OpenAI 兼容接口

## 注意事项

- 爬虫需遵守各平台 robots.txt，已内置请求间隔和重试机制
- AI 评分需要配置 API Key，不配置则使用规则引擎评分
- 微信小程序 webview 需要域名白名单，原帖跳转使用复制链接方式
- MVP 阶段，后续可扩展：用户系统、收藏、发布、地图等
