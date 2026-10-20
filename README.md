# bilibili-mcp

B站（Bilibili）MCP Server：让支持 MCP 的 AI 助手直接操作 B 站，**27 个工具**，覆盖登录、搜索采集、内容发布、数据分析、互动运营。

> 这是 [adoresever/bilibili-mcp](https://github.com/adoresever/bilibili-mcp)（MIT）的修改版，保留原作者的版权声明。
> 非官方项目，与哔哩哔哩无关，仅供学习研究。使用时请遵守 B 站的社区规则和用户协议。

## 和上游相比改了什么

详见 [CHANGES.md](CHANGES.md)。简要说：

| 改动 | 原因 |
|---|---|
| 扫码登录改读响应头 `Set-Cookie`（`mcp_server.py` 的 `_poll_qrcode`、`bili_login_check`，以及 `bili_login.py`） | 2026-10 起 B 站把 Cookie 从响应体挪到了响应头，上游和 `bilibili-api-python 17.4.2` 会保存一份四个字段全空的凭证，并且 `bili_login` 看到文件存在还会说“已登录” |
| `bili_upload_video` / `bili_upload_video_multi` 新增 `ai_declaration`（默认开） | 一键附上创作者声明“该视频使用人工智能合成技术”，对应 `VideoMeta.neutral_mark` |
| 新增 `only_self` 参数 | 往投稿体里加 `is_only_self=1`，用来先仅自己可见地试投 |
| `bili_video_zones` 改为读取 `bilibili-api-python` 缓存的可投稿分区表 | 上游写死的对照有错（例如 208 是“校园学习”，不是“科技”） |
| `requirements.txt` 把 `mcp` 限制在 `<2` | `mcp` 2.x 把 `FastMCP` 改了名，`from mcp.server.fastmcp import FastMCP` 直接报错，服务起不来 |

## 验证状态（如实说明）

| 项目 | 状态 |
|---|---|
| 服务能启动，列出 27 个工具（stdio） | 已验证 |
| 扫码登录读 `Set-Cookie`，得到有效凭证，`bili_check_credential` 通过 | 已验证（2026-10，用的是同样读法的诊断脚本） |
| 通过 `bili_login_check` / `bili_login.py` 完整走完“扫码 → 保存凭证” | **未验证**，只测到“等待扫码”这一步 |
| `bili_video_zones`、投稿体构造（含 `neutral_mark`、`is_only_self`） | 已离线验证 |
| **真实上传** `bili_upload_video` | **未验证，作者没有真实投稿过** |
| AI 声明在服务端是否生效、是否展示 | **未验证** |
| `only_self` 在服务端是否真的设为仅自己可见 | **未验证**。首次投稿后请自己到创作中心核对可见性 |
| 其余上游工具（搜索、评论、字幕、排行等） | 未重新测试，沿用上游 |

## 功能

### 登录认证

| Tool | 功能 | 说明 |
|------|------|------|
| `bili_login` | 扫码登录 | 生成二维码（base64 图片并保存为 `qrcode_login.png`） |
| `bili_login_check` | 登录状态检查 | 轮询扫码状态，成功后保存凭证 |
| `bili_check_credential` | 凭证验证 | 检查当前登录是否有效，返回用户名 |

### 数据采集

| Tool | 功能 | 说明 |
|------|------|------|
| `bili_search` | 搜索视频 | 按关键词搜索，支持按播放量/最新/弹幕排序 |
| `bili_comments` | 获取评论 | 获取视频热门评论，含子评论 |
| `bili_subtitle` | 获取字幕 | 获取视频 AI 字幕 |
| `bili_danmaku` | 获取弹幕 | 获取视频弹幕列表 |
| `bili_video_info` | 视频详情 | 播放量、评论数、收藏数等 |
| `bili_reply` | 回复评论 | 发表评论或回复（支持楼中楼） |
| `bili_crawl` | 批量采集 | 搜索 + 评论 + 字幕一步到位 |

### 内容发布

| Tool | 功能 | 说明 |
|------|------|------|
| `bili_send_dynamic` | 发图文动态 | 文字 / 图文动态，支持定时发布、话题 |
| `bili_upload_video` | 上传视频 | 单 P 视频；本版新增 `ai_declaration`、`only_self` |
| `bili_upload_video_multi` | 多 P 上传 | 多分 P 合并投稿；同样新增上面两个参数 |
| `bili_send_opus` | 图文专栏 | 发布图文长内容 |
| `bili_video_zones` | 分区查询 | 返回可投稿的主分区 → 子分区 ID |

### 数据分析

| Tool | 功能 |
|------|------|
| `bili_hot_videos` / `bili_hot_buzzwords` / `bili_weekly_hot` | 热门视频、热搜词、每周必看 |
| `bili_rank` | 全站及各分区排行榜 |
| `bili_user_info` / `bili_user_videos` | UP 主信息和投稿列表 |

### 互动运营

| Tool | 功能 |
|------|------|
| `bili_favorite_lists` / `bili_favorite_content` | 收藏夹列表和内容 |
| `bili_send_message` | 发私信 |
| `bili_unread_messages` / `bili_received_replies` / `bili_received_at_and_likes` | 未读消息、收到的回复、@和点赞 |

`bili_reply`、`bili_send_message`、`bili_send_dynamic` 会真的发出内容，请谨慎，尤其是让 AI 自动调用时。

## 快速开始

需要 Python 3.10+。作者测试用的是 Python 3.14、`bilibili-api-python 17.4.2`、`aiohttp 3.14`、`mcp 1.30`。

```bash
git clone https://github.com/matkaparka/bilibili-mcp.git
cd bilibili-mcp
python -m venv .venv
.venv/bin/pip install -r requirements.txt        # Windows: .venv\Scripts\pip
```

### 登录

方式一：接入 MCP 后让 AI 调用 `bili_login`，把二维码给你扫，再调用 `bili_login_check` 直到返回 `done`。

方式二：命令行

```bash
.venv/bin/python bili_login.py                   # Windows: .venv\Scripts\python
```

凭证保存在 `bili_credential.json`（已在 `.gitignore` 里）。**不要提交它，也不要发给别人。** 没有 `refresh_token`，过期后需要重新扫码。

### 注册到 MCP 客户端

Claude Code：在项目里建 `.mcp.json`，路径换成你自己的绝对路径。

```json
{
  "mcpServers": {
    "bilibili-mcp": {
      "command": "/path/to/bilibili-mcp/.venv/bin/python",
      "args": ["/path/to/bilibili-mcp/mcp_server.py"]
    }
  }
}
```

Windows 上写成 `E:/path/to/bilibili-mcp/.venv/Scripts/python.exe`。Cursor、Cline、Claude Desktop 等客户端的配置方式类似：command 填 Python，args 填 `mcp_server.py` 的完整路径。

用 MCP Inspector 测试：

```bash
npx @modelcontextprotocol/inspector .venv/bin/python mcp_server.py
```

### 投稿的几个注意事项

- 调用 `bili_upload_video` 时**显式传 `tid`**，默认值 124 是“知识 → 社科·法律·心理”。可用 `bili_video_zones` 查可投稿的子分区。
- 不传 `cover_path` 时，工具会用 `ffmpeg` 从视频第 3 秒截封面，这要求 **MCP 进程的 PATH 里有 `ffmpeg`**。不确定的话直接传 `cover_path`。
- 简介在页面参数上会被截到 250 字。
- AI 生成的内容请保持 `ai_declaration=True`。第一次投稿建议同时传 `only_self=True`，传完到创作中心确认可见性和声明都生效。

## 能在 DeepSeek 里用吗？

这个服务是标准的 stdio MCP 服务，不绑定任何模型。能不能“在 DeepSeek 里用”取决于你用的客户端：

- DeepSeek 的网页和 App 本身不是 MCP 客户端，不能直接挂载。
- **Claude Code + DeepSeek 的 Anthropic 兼容接口**：把 Claude Code 的后端指到 DeepSeek 即可，MCP 工具由 Claude Code 负责调用。环境变量写法（模型名按 DeepSeek 官方文档填，Token 不要写进仓库）：
  ```bash
  export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
  export ANTHROPIC_AUTH_TOKEN=<你的 DeepSeek API Key>
  export ANTHROPIC_MODEL=<DeepSeek 的模型名>
  ```
- 其他支持 MCP、又能接 DeepSeek 的客户端（例如 Cline）原理相同。

**作者没有在 DeepSeek 后端下验证过这些工具的调用是否稳定。** 工具调用的质量取决于模型本身。建议先用只读工具（`bili_check_credential`、`bili_search`）试，确认没问题再让它投稿。

## 技术栈

- [bilibili-api-python](https://github.com/Nemo2011/bilibili-api)：B 站 API 封装
- [MCP Python SDK（FastMCP）](https://github.com/modelcontextprotocol/python-sdk)

## 文件

```
mcp_server.py        MCP Server 主文件（27 个工具）
bili_login.py        命令行扫码登录
requirements.txt     依赖（mcp 限制在 <2）
CHANGES.md           相对上游的改动和验证状态
bili_credential.json 登录凭证（运行后生成，已被 .gitignore 忽略）
```

## 许可证

MIT。原作者 AGI_Ananas 的版权声明保留，修改部分见 [CHANGES.md](CHANGES.md)。
