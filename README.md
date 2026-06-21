# GLaDOS 自动签到

每日自动完成 GLaDOS 签到，支持 GitHub Actions 云端定时运行 + 本地 Python 脚本两种模式，可选 PushPlus 微信推送通知。

---

## Cookie 获取教程

Cookie 是签到的唯一身份凭证，请按以下步骤获取：

1. 用浏览器打开 https://glados.cloud/console/checkin 并**确保已登录**
2. 按 **F12** 打开开发者工具（Edge/Chrome 通用）
3. 点击顶部的 **Network（网络）** 标签
4. 点击页面上的【**签到**】按钮
5. 在 Network 列表中找到名为 `checkin` 的请求，点击它
6. 在右侧 **Headers（标头）** 面板中找到 **Request Headers** 区域
7. 找到 `cookie` 字段，右键复制其**完整内容**

示例格式：`_ga=GA1.2.xxx; _gid=GI1.2.xxx; koa:sess=xxx; koa:sess.sig=xxx`

> 注意：Cookie 有效期有限（通常数周至数月），过期后需重新获取并更新。

---

## 方式一：GitHub Actions（推荐，无需本地运行）

### 第一步：创建仓库

将本项目推送到你的 GitHub 仓库：

```bash
cd D:\LEARN\github\gladosCHECKIN
git init
git add .
git commit -m "Initial commit: GLaDOS auto checkin"
git remote add origin https://github.com/你的用户名/gladosCHECKIN.git
git push -u origin main
```

### 第二步：配置 Secrets

进入 GitHub 仓库页面 → **Settings** → **Secrets and variables** → **Actions** → 点击 **New repository secret**

添加以下 Secrets：

| Secret 名称 | 说明 |
|---|---|
| `GLADOS_COOKIES` | 按上面教程获取的 Cookie 完整内容 |
| `PUSHPLUS_TOKEN` | （可选）在 https://www.pushplus.plus/ 注册后获取的 Token |

### 第三步：触发运行

- **自动运行**：每天北京时间 08:30 自动执行（已在 workflow 中配置）
- **手动运行**：仓库页面 → Actions → 选择 "GLaDOS Auto CheckIn" → 点击 **Run workflow**
- **首次触发**：推送任意代码即可触发第一次运行

> 注意：GitHub Actions 如果仓库 60 天无活动会自动暂停，届时需手动触发一次。

---

## 方式二：本地 Python 脚本

### 安装依赖

```bash
pip install -r requirements.txt
```

### 设置环境变量

**Windows PowerShell（临时，当前窗口有效）：**

```powershell
$env:GLADOS_COOKIES = "你的cookie内容"
$env:PUSHPLUS_TOKEN = "你的pushplus_token"  # 可选
python checkin.py
```

**Windows 系统环境变量（永久）：**

1. 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
2. 新建用户变量，变量名 `GLADOS_COOKIES`，值为你的 Cookie
3. 再新建 `PUSHPLUS_TOKEN`（可选）
4. 重启终端后运行 `python checkin.py`

### 配置 Windows 任务计划程序（本地自动运行）

1. 搜索打开"任务计划程序"
2. 点击"创建基本任务"
3. 名称填 `GLaDOS签到`，下一步
4. 触发器选择"每天"，设置时间（如 08:30），下一步
5. 操作选择"启动程序"，下一步
6. 程序/脚本填 `python`（或 python.exe 完整路径）
7. 添加参数填 `checkin.py`
8. 起始于填 `D:\LEARN\github\gladosCHECKIN`
9. 完成

---

## PushPlus 微信通知（可选）

1. 访问 https://www.pushplus.plus/ 用微信扫码登录
2. 进入个人中心，复制你的 **Token**
3. 将 Token 配置到 GitHub Secret `PUSHPLUS_TOKEN` 或本地环境变量中
4. 签到完成后会自动推送结果到微信

---

## 项目文件结构

```
gladosCHECKIN/
├── checkin.py                      # 签到主脚本
├── requirements.txt                # Python 依赖
├── README.md                       # 本说明文档
└── .github/
    └── workflows/
        └── checkin.yml             # GitHub Actions 配置
```

---

## 常见问题

**Q: 签到失败提示 cookie 无效？**
A: Cookie 已过期，请按教程重新获取并更新 Secret 或环境变量。

**Q: GitHub Actions 60 天后停止了？**
A: 进入仓库 Actions 页面，手动点击 Run workflow 即可恢复。

**Q: 推送通知没收到？**
A: 检查 PushPlus Token 是否正确配置，登录 pushplus.plus 确认服务状态。
