# 花神咖啡馆在线点餐平台

一个基于 **Django REST Framework + Vue 3 + Vite** 的在线点餐平台课程项目。

系统包含顾客端、商家端、配送员端和平台管理端，使用 SQLite 作为默认数据库。当前阶段面向本地开发、课程展示和功能演示。

---

## 主要功能

### 顾客端

* 注册、登录
* 浏览器定位并自动选择最近门店
* 手动切换门店
* 按分类浏览商品
* 商品定制：温度、冰量、杯型
* 加入购物车
* 使用优惠券
* 提交订单
* 模拟支付
* 查看订单
* 评价订单
* 修改个人资料和密码

### 商家端

* 独立商家账号登录
* 查看门店信息
* 添加商品
* 补充库存
* 接单
* 完成制作

### 配送员端

* 独立骑手账号登录
* 查看可接配送订单
* 接单
* 取餐
* 送达

### 平台端

* 管理员登录
* 用户启用 / 禁用
* 商品管理
* 数据统计报表
* 优惠券发放

---

## 核心业务逻辑

### 门店逻辑

* 一个商家账号对应一个门店。
* 顾客选择门店后，只展示该门店的商品。
* 购物车和下单时会校验商品所属门店。
* 购物车中只允许存在同一门店的商品。
* 若购物车已有 A 门店商品，再加入 B 门店商品，后端会返回错误提示。
* 用户需要先清空购物车，再切换门店重新点单。

### 商品定制逻辑

商品支持以下定制项：

* 温度
* 冰量
* 杯型

其中，中杯和大杯会影响商品价格。定制信息会保存到购物车和订单明细中。

---

## 技术栈

### 后端

* Python
* Django 5
* Django REST Framework
* SQLite

### 前端

* Vue 3
* Vue Router
* Axios
* Vite

### 认证方式

课程 MVP 阶段使用 `user_id` 参数模拟当前登录用户，暂未接入正式 Token / JWT / Session 权限体系。

---

## 项目结构

```text
order_Platform/
+-- manage.py
+-- db.sqlite3
+-- order_Platform/          # Django 项目配置
+-- users/                   # 用户、门店、平台、优惠券相关接口
+-- dishes/                  # 商品模型、商品接口、初始化测试数据命令
+-- cart/                    # 购物车与商品定制
+-- orders/                  # 订单与订单明细
+-- payments/                # 模拟支付
+-- merchant/                # 商家端接口
+-- delivery/                # 配送员端接口
+-- reviews/                 # 评价接口
+-- frontend/                # Vue + Vite 前端
```

---

## 环境要求

建议版本：

* Python 3.10 或更高
* Node.js 18 或更高
* npm 9 或更高

后端依赖：

```powershell
pip install django djangorestframework
```

前端依赖在 `frontend/package.json` 中声明，主要包括：

* `vue`
* `vue-router`
* `axios`
* `vite`
* `@vitejs/plugin-vue`

---

## 首次安装

进入项目根目录：

```powershell
cd <项目根目录>
```

### Windows PowerShell

创建并启用 Python 虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install django djangorestframework
```

如果 PowerShell 无法启用虚拟环境，可以临时执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

然后重新启用虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install django djangorestframework
```

### 安装前端依赖

进入前端目录并安装依赖：

```powershell
cd frontend
npm install
cd ..
```

---

## 数据库初始化

项目默认使用 SQLite，数据库文件为：

```text
db.sqlite3
```

首次运行或数据库结构更新后，在项目根目录执行：

```powershell
python manage.py migrate
python manage.py init_test_data
```

`init_test_data` 命令可重复执行，会创建或更新测试账号、门店和测试商品。

---

## 启动后端

在项目根目录执行：

```powershell
python manage.py runserver 127.0.0.1:8000
```

如果当前环境已经有 `.venv`，但本机 Python 无法直接加载依赖，可以临时使用：

```powershell
$env:PYTHONPATH='.venv\Lib\site-packages'
python manage.py runserver 127.0.0.1:8000
```

---

## 启动前端

另开一个终端窗口，进入前端目录：

```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5175
```

前端默认通过 Vite 代理把 `/api` 请求转发到：

```text
http://127.0.0.1:8000
```

请先启动后端，再启动前端。

---

## 访问地址和测试账号

### 顾客端

访问地址：

```text
http://127.0.0.1:5175/login
```

测试账号：

```text
customer / 123456
```

### 商家端

访问地址：

```text
http://127.0.0.1:5175/merchant/login
```

测试账号：

```text
merchant / 123456
merchant_west / 123456
merchant_tech / 123456
```

### 配送员端

访问地址：

```text
http://127.0.0.1:5175/delivery/login
```

测试账号：

```text
driver / 123456
```

### 平台端

访问地址：

```text
http://127.0.0.1:5175/platform/login
```

测试账号：

```text
admin / 123456
```

---

## 推荐演示流程

### 顾客端演示流程

1. 登录 `customer / 123456`。
2. 进入首页，允许浏览器定位。
3. 系统自动选择最近门店。
4. 点击当前门店卡片，手动切换门店。
5. 进入点单页，选择商品分类。
6. 进入商品详情页，选择温度、冰量、杯型。
7. 加入购物车。
8. 在购物车选择优惠券并提交订单。
9. 进入支付页，点击模拟支付成功。
10. 在“我的订单”中查看订单状态和商品定制信息。

### 商家端演示流程

1. 登录某个商家账号，例如 `merchant / 123456`。
2. 在工作台查看该账号对应门店的名称、地址和经纬度。
3. 在进货页添加商品或补充库存。
4. 顾客支付后，在接单页接单并完成制作。

### 配送员端演示流程

1. 登录 `driver / 123456`。
2. 查看新的配送任务。
3. 接单。
4. 取餐。
5. 送达。

### 平台端演示流程

1. 登录 `admin / 123456`。
2. 查看用户、商品、报表和优惠券信息。
3. 启用或禁用用户。
4. 管理商品状态。
5. 向用户发放优惠券。

---

## 常用检查命令

### 后端检查

在项目根目录执行：

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
```

### 前端构建

进入前端目录：

```powershell
cd frontend
npm run build
```

### 前端本地预览构建产物

```powershell
npm run preview
```

---

## 重要数据命令

### 重建或刷新测试数据

```powershell
python manage.py init_test_data
```

### 重新应用数据库迁移

```powershell
python manage.py migrate
```

### 清空数据库并重新初始化

删除 `db.sqlite3` 后执行：

```powershell
python manage.py migrate
python manage.py init_test_data
```

注意：删除 `db.sqlite3` 会清除所有本地订单、购物车、支付、评价等数据。

---

## 已知问题和说明

### 1. 当前配置仅用于开发和课程演示

当前项目配置包含：

* `DEBUG=True`
* 开发用 `SECRET_KEY`
* SQLite 数据库
* 未配置生产环境静态资源部署

请勿直接用于真实线上系统。

### 2. 登录方式为 MVP 模拟方案

当前后端接口主要通过 `user_id` 参数识别当前用户。

暂未实现：

* JWT
* Token
* Session 权限体系
* 完整角色鉴权

### 3. 支付为模拟支付

支付页只创建模拟支付记录。

点击支付成功后，系统会：

* 将 `Payment.status` 改为 `success`
* 将订单状态改为 `paid`

当前未接入微信、支付宝或银行卡支付。

### 4. 浏览器定位依赖权限

顾客首页会调用浏览器 Geolocation API。

在以下环境通常可用：

* `127.0.0.1`
* `localhost`
* HTTPS 环境

如果用户拒绝定位权限，系统会使用默认门店或已保存门店。

### 5. 门店信息存放在商家用户上

一个商家账号对应一个门店。

门店相关字段位于 `users.User`，包括：

* 门店名
* 文字地址
* 经度
* 纬度

如果商家端显示“未设置”，请先在项目根目录执行：

```powershell
python manage.py migrate
python manage.py init_test_data
```

### 6. 前端开发端口说明

`vite.config.js` 默认端口可能是：

```text
5173
```

本文档推荐使用：

```text
5175
```

这是为了和开发过程中的演示地址保持一致。

两个端口都可以使用，只要浏览器访问的端口和实际启动端口一致即可。

### 7. 当前未提供 requirements.txt

后端依赖较少，可以按本文档手动安装：

```powershell
pip install django djangorestframework
```

如需固定依赖版本，可在虚拟环境中执行：

```powershell
pip freeze > requirements.txt
```

之后其他环境可使用：

```powershell
pip install -r requirements.txt
```

### 8. Vite 构建权限问题

在某些受限沙箱、同步盘或权限受限目录中，`npm run build` 可能因为无法写入 `node_modules/.vite-temp` 而失败。

建议在普通本地项目目录中运行，并确认项目目录和 `node_modules` 具有写入权限。

---

## 开发提示

每次拉取新代码后，建议执行：

```powershell
python manage.py migrate
python manage.py init_test_data
```

如果前端依赖发生变化，进入 `frontend` 目录执行：

```powershell
npm install
```

如果页面请求失败，优先检查：

1. 后端是否运行在 `127.0.0.1:8000`
2. 前端是否运行在当前访问的端口
3. Vite 代理是否正确转发 `/api`
4. 数据库是否已经执行 `migrate`
5. 是否已经运行 `init_test_data`
