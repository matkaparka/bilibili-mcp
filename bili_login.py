#!/usr/bin/env python3
"""B站扫码登录（命令行版），保存凭证供 MCP Server 使用。

说明：2026-10 起，B 站在扫码成功后把 Cookie 放在 poll 响应的 Set-Cookie 头里，响应体里只剩
ticket。bilibili-api-python 17.x 的 QrCodeLogin.check_state / get_credential 仍按旧格式从响应
体里取，会得到四个空字段并照样保存。这里复用 mcp_server.py 里的 _poll_qrcode 直接读 Set-Cookie，
并且在取不到关键 Cookie 时拒绝保存。
"""

import asyncio
import json
import sys

from bilibili_api.login_v2 import QrCodeLogin, QrCodeLoginEvents

from mcp_server import CRED_FILE, _poll_qrcode

REQUIRED = ("SESSDATA", "bili_jct", "DedeUserID")


async def main() -> int:
    qr = QrCodeLogin()
    await qr.generate_qrcode()
    print(qr.get_qrcode_terminal())
    print("\n请用B站App扫描上方二维码（180秒内有效）\n")

    last = None
    while True:
        state, cookies = await _poll_qrcode(qr)
        if state != last:
            if state == QrCodeLoginEvents.SCAN:
                print("等待扫码...")
            elif state == QrCodeLoginEvents.CONF:
                print("已扫码，请在手机上点确认...")
            last = state
        if state == QrCodeLoginEvents.TIMEOUT:
            print("二维码超时，请重新运行")
            return 1
        if state == QrCodeLoginEvents.DONE:
            break
        await asyncio.sleep(2)

    if not all(cookies.get(k) for k in REQUIRED):
        print("扫码已确认，但 B 站响应里没有 SESSDATA / bili_jct / DedeUserID，未保存凭证。接口可能又变了。")
        return 1

    with open(CRED_FILE, "w") as f:
        json.dump({
            "sessdata": cookies["SESSDATA"],
            "bili_jct": cookies["bili_jct"],
            "buvid3": cookies.get("buvid3", ""),
            "dedeuserid": cookies["DedeUserID"],
        }, f)
    print(f"\n登录成功，凭证已保存到 {CRED_FILE}（不要提交到 git，也不要发给别人）")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
