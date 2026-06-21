# GLaDOS Auto CheckIn

> 基于 Python + GitHub Actions 的 GLaDOS 每日自动签到工具，支持微信通知推送。

## 功能特性

- 每日自动签到，支持 GitHub Actions 云端定时与本地运行两种模式
- 多域名自动容错（glados.rocks / cloud / one / space），任一站点不可用时自动切换
- 签到失败自动重试（最多 3 轮，每轮遍历所有域名）
- 可选 PushPlus 微信推送，签到结果直达手机
- 智能通知标题：区分"签到成功 / 今日已签到 / 签到失败"，并显示剩余天数

## 快速开始

### 1. 获取 Cookie

Cookie 是签到的唯一身份凭证。

1. 用浏览器打开 https://glados.cloud/console/checkin 并确保已登录
2. 按 `F12` 打开开发者工具（Edge / Chrome 通用）
3. 切换到 **Network** 标签
4. 点击页面上的【签到】按钮
5. 在 Network 列表中找到 `checkin` 请求并点击
6. 在 **Request Headers** 中找到 `cookie` 字段，复制完整内容

示例格式：`_ga=GA1.2.xxx; _gid=GI1.2.xxx; koa:sess=xxx; koa:sess.sig=xxx`

> Cookie 有效期通常为数周至数月，过期后需重新获取并更新。

### 2. 部署方式

**方式一：GitHub Actions（推荐）**

Fork 本仓库到你的 GitHub 账号（点击右上角 Fork 按钮），然后进入 **你自己的仓库** 页面，找到 **Settings → Secrets and variables → Actions**，点击 **New repository secret** 添加：

| Secret 名称 | 必填 | 说明 |
|---|---|---|
| `GLADOS_COOKIES` | 是 | 上一步获取的 Cookie 完整内容 |
| `PUSHPLUS_TOKEN` | 否 | PushPlus 推送 Token（见下方配置说明） |

配置完成后，Workflow 会在每天 **北京时间 08:30** 自动执行。你也可以在 Actions 页面点击 **Run workflow** 手动触发。

首次部署后推送任意 commit 即可触发第一次运行。

> GitHub Actions 在仓库 60 天无活动后会自动暂停，届时手动 Run workflow 一次即可恢复。

**方式二：本地运行**

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量并运行
# Linux / macOS
export GLADOS_COOKIES="你的cookie"
export PUSHPLUS_TOKEN="你的token"  # 可选
python checkin.py

# Windows PowerShell
$env:GLADOS_COOKIES = "你的cookie"
$env:PUSHPLUS_TOKEN = "你的token"  # 可选
python checkin.py
```

如需本地定时运行，可配置 Windows 任务计划程序或 Linux crontab，指向 `checkin.py` 即可。

### 3. 微信通知（可选）

1. 访问 https://www.pushplus.plus/ ，微信扫码登录
2. 在个人中心复制你的 Token
3. 配置到 GitHub Secret `PUSHPLUS_TOKEN` 或本地同名环境变量中

签到完成后，结果会自动通过 PushPlus 公众号推送到微信。

## 配置参数

脚本顶部的以下常量可按需调整：

| 参数 | 默认值 | 说明 |
|---|---|---|
| `DOMAINS` | 4 个域名 | API 域名列表，按优先级排列 |
| `MAX_RETRIES` | 3 | 签到失败时最大重试轮数 |
| `RETRY_INTERVAL` | 30 | 每轮重试间隔（秒） |

## 环境变量

| 变量名 | 必填 | 说明 |
|---|---|---|
| `GLADOS_COOKIES` | 是 | GLaDOS 登录 Cookie |
| `PUSHPLUS_TOKEN` | 否 | PushPlus 推送 Token |

## 项目结构

```
├── checkin.py                    # 签到脚本
├── requirements.txt              # Python 依赖
├── README.md                     # 本文档
└── .github/
    └── workflows/
        └── checkin.yml           # GitHub Actions 定时任务
```

## 常见问题

**签到失败提示 Cookie 无效？**
Cookie 已过期，请重新获取并更新 Secret 或环境变量。

**GitHub Actions 超过 60 天停止运行？**
进入仓库 Actions 页面，手动 Run workflow 一次即可恢复自动调度。

**微信没有收到通知？**
确认 PushPlus Token 配置正确，并已关注 PushPlus 公众号。

---

## 免责声明

1. 本项目仅供学习交流使用，使用者应自行遵守 GLaDOS 的服务条款及相关使用规定。
2. 本项目与 GLaDOS 官方无任何关联，不是官方提供的工具。
3. 使用本项目产生的一切后果（包括但不限于账号封禁、数据丢失、服务中断等）由使用者自行承担，作者不承担任何责任。
4. GLaDOS 的 API 接口、域名及服务策略可能随时变更，本项目不保证长期可用性，亦不提供任何形式的担保。
5. Cookie 属于敏感凭证，请妥善保管，切勿泄露。因 Cookie 泄露导致的损失与本项目无关。
6. 请在遵守当地法律法规的前提下使用本项目。
