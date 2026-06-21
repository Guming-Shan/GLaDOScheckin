#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GLaDOS 自动签到脚本
支持本地运行 & GitHub Actions 两种模式
支持 PushPlus 微信推送通知
"""

import os
import json
import time
import random
import logging
import requests
from datetime import datetime, timezone, timedelta

# ========================= 配置区域 =========================

# 从环境变量读取 Cookie（GitHub Actions 中使用 Secret 注入）
COOKIES = os.environ.get("GLADOS_COOKIES", "")

# PushPlus 推送配置（可选）
# 在 https://www.pushplus.plus/ 注册获取 token
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

# GLaDOS API 域名列表（按优先级排列，若第一个失败会自动尝试下一个）
DOMAINS = [
    "https://glados.rocks",
    "https://glados.cloud",
    "https://glados.one",
    "https://glados.space",
]

# 请求头
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]

# ========================= 日志配置 =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ========================= 核心逻辑 =========================


def get_headers(domain: str) -> dict:
    """构造请求头"""
    return {
        "cookie": COOKIES,
        "referer": f"{domain}/console/checkin",
        "origin": domain,
        "user-agent": random.choice(USER_AGENTS),
        "content-type": "application/json;charset=UTF-8",
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    }


def checkin(domain: str) -> dict:
    """执行签到请求"""
    url = f"{domain}/api/user/checkin"
    headers = get_headers(domain)
    payload = {"token": "glados.one"}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return {"success": True, "data": result, "domain": domain}
    except requests.exceptions.RequestException as e:
        logger.warning(f"签到请求失败 ({domain}): {e}")
        return {"success": False, "error": str(e), "domain": domain}


def get_user_status(domain: str) -> dict:
    """获取用户账户状态"""
    url = f"{domain}/api/user/status"
    headers = get_headers(domain)

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        return {"success": True, "data": result}
    except requests.exceptions.RequestException as e:
        logger.warning(f"获取状态失败 ({domain}): {e}")
        return {"success": False, "error": str(e)}


def try_checkin() -> dict:
    """尝试所有域名进行签到"""
    for domain in DOMAINS:
        logger.info(f"尝试签到域名: {domain}")
        result = checkin(domain)
        if result["success"]:
            return result
        # 失败后短暂等待再试下一个域名
        time.sleep(2)

    return {"success": False, "error": "所有域名均签到失败"}


def try_get_status(domain: str = None) -> dict:
    """尝试获取用户状态"""
    domains_to_try = [domain] if domain else DOMAINS
    for d in domains_to_try:
        result = get_user_status(d)
        if result["success"]:
            return result
        time.sleep(1)
    return {"success": False, "error": "无法获取用户状态"}


def format_message(checkin_result: dict, status_result: dict) -> str:
    """格式化签到结果消息"""
    cst = timezone(timedelta(hours=8))
    now = datetime.now(cst).strftime("%Y-%m-%d %H:%M:%S")

    lines = [f"GLaDOS 签到报告", f"时间: {now}", ""]

    if checkin_result["success"]:
        data = checkin_result["data"]
        msg = data.get("message", data.get("msg", "未知"))
        # 解析签到返回信息
        if "Checkin" in msg or "checkin" in msg.lower():
            lines.append(f"签到结果: {msg}")
        elif data.get("code") == 0 or data.get("code") == 1:
            lines.append(f"签到结果: {msg}")
        else:
            lines.append(f"签到结果: {msg}")
            lines.append(f"返回数据: {json.dumps(data, ensure_ascii=False)}")
    else:
        lines.append(f"签到结果: 失败")
        lines.append(f"错误信息: {checkin_result.get('error', '未知错误')}")

    if status_result.get("success"):
        sdata = status_result["data"]
        if isinstance(sdata, dict) and "data" in sdata:
            info = sdata["data"]
        else:
            info = sdata

        if isinstance(info, dict):
            left = info.get("leftDays", info.get("left_days", "未知"))
            plan = info.get("plan", info.get("planName", "未知"))
            lines.append(f"套餐: {plan}")
            lines.append(f"剩余天数: {left}")

    return "\n".join(lines)


def build_title(checkin_result: dict, status_result: dict) -> str:
    """根据签到结果和账户状态动态生成通知标题"""
    if not checkin_result["success"]:
        return f"GLaDOS 签到失败 - {checkin_result.get('error', '未知错误')[:40]}"

    # 解析 API 返回的 message
    data = checkin_result["data"]
    msg = data.get("message", data.get("msg", ""))
    code = data.get("code", -1)

    # 判断签到状态并生成对应标题
    if "already" in msg.lower() or "tomorrow" in msg.lower() or "logged" in msg.lower():
        # 今天已经签到过了
        title = "GLaDOS 今日已签到"
    elif "Checkin" in msg or code == 0:
        # 新签到成功
        title = "GLaDOS 签到成功"
    else:
        title = f"GLaDOS 签到 - {msg[:30]}" if msg else "GLaDOS 签到完成"

    # 追加剩余天数信息
    if status_result.get("success"):
        sdata = status_result["data"]
        info = sdata.get("data", sdata) if isinstance(sdata, dict) else sdata
        if isinstance(info, dict):
            left = info.get("leftDays", info.get("left_days"))
            if left is not None:
                title += f" (剩余{left}天)"

    return title


def push_plus_notify(title: str, content: str):
    """通过 PushPlus 发送微信通知"""
    if not PUSHPLUS_TOKEN:
        logger.info("未配置 PushPlus Token，跳过通知推送")
        return

    url = "http://www.pushplus.plus/send"
    payload = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content.replace("\n", "<br>"),
        "template": "html",
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        result = response.json()
        if result.get("code") == 200:
            logger.info("PushPlus 通知发送成功")
        else:
            logger.warning(f"PushPlus 通知发送失败: {result.get('msg', '未知')}")
    except Exception as e:
        logger.warning(f"PushPlus 通知请求异常: {e}")


# ========================= 主函数 =========================


def main():
    logger.info("=" * 40)
    logger.info("GLaDOS 自动签到开始")
    logger.info("=" * 40)

    # 检查 Cookie
    if not COOKIES:
        error_msg = (
            "未配置 GLADOS_COOKIES 环境变量！\n"
            "请设置环境变量后重试。\n\n"
            "获取方法：\n"
            "1. 用浏览器打开 https://glados.cloud/console/checkin\n"
            "2. 按 F12 打开开发者工具\n"
            "3. 切换到 Network(网络) 标签\n"
            "4. 点击页面上的【签到】按钮\n"
            "5. 在 Network 中找到 checkin 请求\n"
            "6. 点击该请求，查看 Request Headers\n"
            "7. 复制 Cookie 字段的完整内容"
        )
        logger.error(error_msg)
        push_plus_notify("GLaDOS 签到失败", error_msg)
        return

    # 随机延迟（GitHub Actions 中避免同一时间大量请求）
    delay = random.randint(0, 300)
    logger.info(f"随机延迟 {delay} 秒后开始签到...")
    time.sleep(delay)

    # 执行签到
    checkin_result = try_checkin()

    # 获取签到域名用于状态查询
    domain = checkin_result.get("domain")
    status_result = try_get_status(domain)

    # 格式化消息
    message = format_message(checkin_result, status_result)

    # 输出结果
    logger.info("-" * 40)
    for line in message.split("\n"):
        logger.info(line)
    logger.info("-" * 40)

    # 推送通知
    title = build_title(checkin_result, status_result)
    push_plus_notify(title, message)

    logger.info("GLaDOS 自动签到完成")


if __name__ == "__main__":
    main()
