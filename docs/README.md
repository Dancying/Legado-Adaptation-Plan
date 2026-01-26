# 项目结构

```text
Legado-Adaptation-Plan/
├── .gitignore
├── config.py                       # 项目全局配置
├── Dockerfile                      # 容器化定义
├── LICENSE                         # 开源协议
├── main.py                         # 程序入口
├── README.md                       # 项目说明文档
├── requirements.txt                # 项目依赖
├── app/                            # Web 服务逻辑
│   ├── __init__.py
│   ├── routes.py                   # API 路由接口
│   └── templates/                  # HTML 模板文件
│       ├── 404.html
│       └── index.html
├── core/                           # 核心业务逻辑
│   ├── __init__.py
│   ├── engine/                     # 运行引擎
│   │   ├── __init__.py
│   │   ├── browser_launcher.py     # 浏览器启动管理
│   │   ├── browser_operator.py     # 页面自动化操作
│   │   └── source_manager.py       # 书源管理逻辑
│   └── scrapers/                   # 网站爬虫解析器
│       ├── __init__.py
│       ├── base.py                 # 爬虫基类
│       ├── piaotian.py
│       ├── shuba.py
│       ├── shux.py
│       └── twkan.py
├── docs/                           # 项目文档与图片
│   ├── Book Source Tutorial.md     # 书源制作教程
│   └── images/                     # 文档辅助图片
│       └── (多张说明图...)
├── res/                            # 书源 JSON 文件
│   ├── BookSource_101KANSHU.json
│   ├── BookSource_69SHUBA.json
│   ├── ...
│   └── BookSource_TWKAN_PROXY.json
├── scripts/                        # 独立维护脚本
│   └── clean_source.py             # JSON 清理美化工具
├── temp/                           # 临时文件夹 (自动生成)
├── tests/                          # 手动测试脚本
│   ├── __init__.py
│   ├── test_browser.py
│   ├── test_logger.py
│   ├── test_scraper.py
│   └── test_source.py
└── utils/                          # 通用工具函数
    ├── __init__.py
    ├── file_io.py                  # 文件读写工具
    ├── logger.py                   # 日志配置工具
    └── network.py                  # 负责网络请求
```
