# 相对上游的改动

上游：[adoresever/bilibili-mcp](https://github.com/adoresever/bilibili-mcp)（MIT，Copyright (c) 2026 AGI_Ananas）。
下面的函数名以 `mcp_server.py` 为准，行号会随版本变化。

## 1. 扫码登录读 `Set-Cookie`

- **现象**：扫码确认后 `bili_login_check` 返回 `done`，但保存的 `bili_credential.json` 四个字段全是空串；之后 `bili_login` 看到文件存在，会返回 `already_logged_in`。
- **原因**：B 站的 `passport-login/web/qrcode/poll` 在 2026-10 的实测里，响应体的 `url` 只有 `ticket`（`passport.biligame.com/.../crossDomain?ticket=…`），`refresh_token` 为空；`SESSDATA`、`bili_jct`、`DedeUserID`、`DedeUserID__ckMd5`、`sid` 放在响应头 `Set-Cookie` 里。`bilibili-api-python 17.4.2` 的 `QrCodeLogin.check_state` 按旧格式从响应体取字段，所以得到空串。
- **改法**：新增 `_poll_qrcode`，直接请求同一个 poll 接口并读 `Set-Cookie`；`bili_login_check` 改用它；取不到三个关键 Cookie 时返回 `no_cookie`，不再保存空文件。`bili_login.py` 同步修改。
- **没验证到的**：`_poll_qrcode` 在新二维码上返回过“等待扫码”；“扫码成功后经本函数保存凭证”这一支没有端到端跑过。同样的读法在诊断脚本里拿到了五个 Cookie，并通过了 `bili_check_credential`。
- 另外把上游的提示文案改正：`SCAN` 状态是“还没扫”，不是“已扫码”。

## 2. AI 声明：`ai_declaration`

- `bili_upload_video`、`bili_upload_video_multi` 新增 `ai_declaration: bool = True`。
- 开启时把 `VideoMeta.neutral_mark` 设为「作者声明：该视频使用人工智能合成技术」。这串文字来自 `bilibili-api-python` 缓存的创作中心“创作者声明”选项（`data/video_uploader_meta_pre.json` → `neutral_mark.marks[0]`）。
- **没验证**：B 站服务端是否接受、是否展示。上游库的注释对这个字段写的是“不知道能不能随便写文本”。

## 3. 仅自己可见：`only_self`

- 新增 `only_self: bool = False`。通过子类 `_Meta(VideoMeta)` 在投稿体里加 `is_only_self=1`（`VideoMeta` 本身没有这个字段；biliup 的投稿体里有）。
- 离线确认过投稿体里确实带上了字段。**没验证**服务端是否按它设为仅自己可见，首次投稿后请自己核对。

## 4. 分区表

- `bili_video_zones` 改为读 `bilibili-api-python` 缓存的“可投稿分区表”（`data/video_uploader_meta_pre.json` → `tid_list`），返回 `{主分区: {子分区ID: 名称}}`。
- 上游写死的对照有错：例如 208 是“校园学习”，上游写成“科技”；209 是“职业职场”，上游写成“手工”。`bili_upload_video` 的 `tid` 说明同步更新。
- 这份表是库里缓存的，不是实时从 B 站拉的。

## 5. 依赖

- `requirements.txt`：`mcp>=1.0.0` → `mcp>=1.0.0,<2`。`mcp` 2.x 里没有 `mcp.server.fastmcp`，会 `ModuleNotFoundError`。

## 没有改动的

- 其余工具（搜索、评论、字幕、弹幕、排行、收藏夹、私信等）沿用上游，没有重新测试。
- 上游仓库里带的 `bili_credential.json.bak` 没有放进这个仓库。
