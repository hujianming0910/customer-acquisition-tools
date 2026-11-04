# D4Vinci/Scrapling

- 来源记录：抖音 @📷大声发《掌握信息差就站在了食物链顶端》
  视频 https://www.douyin.com/video/7702774431202267850（短链 https://v.douyin.com/RUjgXuGyEx4/）
  发现日期：2026-11-05｜由大哥转豆包分析后派牛牛核实
  核实状态：已看视频确认（页面关键词/评论为 `scrapling`、`scrapling反扒能力`、`scrapling技能下载`，对上 `D4Vinci/Scrapling`）
  可用状态：已本地跑通（报告：`GitHub工具试用/报告_D4Vinci__Scrapling_20261105.md`）

- 仓库：https://github.com/D4Vinci/Scrapling
- 分类：自动化与采集（`automation`）
- 一句话：自适应网页抓取框架，支持 HTTP、真实浏览器、Cloudflare/WAF 反爬、JS 渲染、并发爬虫和结构化解析。
- Stars：96,131（2026-11-05 核查）
- Forks：10,078
- 最近提交：2026-11-04
- License：BSD-3-Clause
- 免费级别：F0（BSD-3-Clause，开源）
- 部署：Python / pip / Docker
- 中国可用：已实测可本地运行；macOS 12 不能跑 `scrapling install`，浏览器抓取改用本机 Chrome + `--real-chrome`
- 适用场景：西门子/施耐德/ABB 等公开产品页配图直链批量提取；结构会变的行业目录、招标公告、公开图库页面；需要过 Cloudflare/WAF 的公开页面。
- 风险/限制：反爬能力是双刃剑，必须遵守目标站条款和 robots.txt；不绕登录、不破验证码、不抓个人隐私；Cloudflare 通过可能很慢（本次 191 秒）；不是开箱即用的获客成品，需要写脚本或让 Agent 生成脚本。
- 评分：**84**（场景 26 / 维护 20 / 免费 15 / 部署 11 / 合规 6 / 中国 6）
- 级别：**P0**
- 证据：https://github.com/D4Vinci/Scrapling · https://github.com/D4Vinci/Scrapling/releases/tag/v0.5 · https://github.com/D4Vinci/Scrapling/blob/main/LICENSE
- 实测：人民网首页 0.17s / 200 / 105 个图片链接；西门子 S7-1200 G2 产品页 0.88s / 200 / 9 个图片直链；nowsecure.nl Cloudflare 测试页 200 / 190.99s；gkong 搜索普通请求被 BotChallenge 拦截，`StealthyFetcher + real_chrome + solve_cloudflare` 过挑战后目标站返回 504。
- 备注：官方自带 `agent-skill/Scrapling-Skill`，已装到 Codex 的 `~/.codex/skills/scrapling-official`；第三方封装版在 `~/.codex/skills/scrapling`。优先用官方版，API 更贴当前 0.5。
