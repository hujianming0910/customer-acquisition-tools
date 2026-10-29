#!/usr/bin/env python3
"""Build catalog.json, TOOLS.md, category pages and tool pages from the verified snapshot."""

import json
import os
import shutil


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAPSHOT = os.path.join(ROOT, "data", "github_meta_snapshot_20261030.json")
SEED = os.path.join(ROOT, "scripts", "seed_tools.tsv")
VERIFIED_AT = "2026-10-30"

CATEGORIES = [
    {"id": "lead-discovery", "name": "线索发现", "purpose": "找企业、找招标、找行业目录、监控目标页面"},
    {"id": "lead-database", "name": "线索整理与数据库", "purpose": "把散乱线索变成可筛选、可去重、可协作的表"},
    {"id": "crm", "name": "开源 CRM", "purpose": "客户、公司、商机、跟进阶段管理"},
    {"id": "outreach", "name": "触达与官网承接", "purpose": "表单留资、在线客服、邮件自动化、预约"},
    {"id": "seo-content", "name": "内容与 SEO", "purpose": "官网内容、博客、落地页、搜索曝光"},
    {"id": "automation", "name": "自动化与采集", "purpose": "浏览器自动化、网页采集、工作流编排"},
    {"id": "analytics", "name": "网站分析", "purpose": "访问来源、落地页、转化和用户行为"},
    {"id": "data-cleaning", "name": "数据清洗", "purpose": "去重、标准化、邮箱验证、表格整理"},
    {"id": "reference", "name": "资源索引", "purpose": "找更多可自托管工具和替代方案"},
]

LEVEL_ORDER = {"P0": 0, "P1": 1, "P2": 2, "拒绝": 3}


def level_for(score):
    if score >= 80:
        return "P0"
    if score >= 65:
        return "P1"
    if score >= 50:
        return "P2"
    return "拒绝"


def read_seed():
    rows = []
    with open(SEED, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|")
            if len(parts) != 15:
                raise ValueError(f"bad seed row ({len(parts)} fields): {line[:80]}")
            rows.append(parts)
    return rows


def build():
    raw = json.load(open(SNAPSHOT, encoding="utf-8"))
    meta_by_name = {x["full_name"].lower(): x for x in raw}
    cat_name = {x["id"]: x["name"] for x in CATEGORIES}
    tools = []

    for row in read_seed():
        (full_name, cat, score, s1, s2, s3, s4, s5, s6,
         free_level, free_note, deploy, china, use_case, risk) = row
        repo = meta_by_name.get(full_name.lower())
        if not repo:
            raise ValueError(f"metadata missing for {full_name}; add it to the snapshot first")
        license_id = (repo.get("license") or {}).get("spdx_id") or "NOASSERTION"
        if license_id == "NOASSERTION":
            license_id = "自定义/多许可（读 LICENSE）"
        score = int(score)
        tools.append({
            "id": full_name.lower().replace("/", "__"),
            "name": full_name.split("/")[1],
            "full_name": full_name,
            "url": repo["html_url"],
            "description_en": repo.get("description") or "",
            "description_zh": use_case,
            "category": cat,
            "stars": repo["stargazers_count"],
            "forks": repo["forks_count"],
            "open_issues": repo["open_issues_count"],
            "pushed_at": repo["pushed_at"],
            "language": repo.get("language") or "",
            "license": license_id,
            "free_level": free_level,
            "free_note": free_note,
            "deploy": deploy,
            "china_access": china,
            "use_case": use_case,
            "risk": risk,
            "score": score,
            "score_parts": {
                "场景匹配": int(s1), "维护活跃": int(s2), "免费许可": int(s3),
                "部署可控": int(s4), "数据合规": int(s5), "中国可用": int(s6),
            },
            "level": level_for(score),
            "verified_at": VERIFIED_AT,
            "evidence_urls": [repo["html_url"], repo["html_url"] + "/releases"],
            "tags": repo.get("topics") or [],
        })

    tools.sort(key=lambda x: (LEVEL_ORDER[x["level"]], -x["score"], -x["stars"]))
    catalog = {
        "meta": {
            "name": "客户获取工具库",
            "repo": "https://github.com/hujianming0910/customer-acquisition-tools",
            "generated_at": VERIFIED_AT,
            "verified_at": VERIFIED_AT,
            "total": len(tools),
            "p0": sum(1 for x in tools if x["level"] == "P0"),
            "p1": sum(1 for x in tools if x["level"] == "P1"),
            "p2": sum(1 for x in tools if x["level"] == "P2"),
            "rejected": sum(1 for x in tools if x["level"] == "拒绝"),
            "note": "种子目录，由牛牛核验 GitHub API 元数据；豆包分批扩展。Stars/最近提交为 2026-10-30 快照。",
        },
        "categories": CATEGORIES,
        "tools": tools,
    }
    json.dump(catalog, open(os.path.join(ROOT, "catalog.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    lines = [
        "# 工具总表", "",
        f"> 共 {len(tools)} 个工具；P0 {catalog['meta']['p0']} / P1 {catalog['meta']['p1']} / P2 {catalog['meta']['p2']}。"
        "Stars 与最近提交为 2026-10-30 核验快照。", "",
        "| 级别 | 工具 | 分类 | Stars | 最近提交 | License | 免费 | 一句话 |",
        "|---|---|---|---:|---|---|---|---|",
    ]
    for t in tools:
        lines.append(
            f"| **{t['level']}** | [{t['full_name']}]({t['url']}) | {cat_name[t['category']]} | "
            f"{t['stars']:,} | {t['pushed_at'][:10]} | {t['license']} | {t['free_level']} | {t['description_zh']} |"
        )
    lines += ["", "## 分级说明", "",
              "- **P0**：≥80 分，优先做 30–60 分钟最小验证。",
              "- **P1**：65–79 分，按需评估。",
              "- **P2**：50–64 分，观察。",
              "- 评分表见 [CONTRIBUTING.md](CONTRIBUTING.md)。", ""]
    open(os.path.join(ROOT, "TOOLS.md"), "w", encoding="utf-8").write("\n".join(lines))

    os.makedirs(os.path.join(ROOT, "categories"), exist_ok=True)
    for c in CATEGORIES:
        arr = [t for t in tools if t["category"] == c["id"]]
        lines = [f"# {c['name']}", "", c["purpose"], "", f"共 {len(arr)} 个。", "",
                 "| 级别 | 工具 | Stars | 最近提交 | 免费 | 适用场景 |",
                 "|---|---|---:|---|---|---|"]
        for t in arr:
            lines.append(
                f"| **{t['level']}** | [{t['full_name']}]({t['url']}) | {t['stars']:,} | "
                f"{t['pushed_at'][:10]} | {t['free_level']} | {t['use_case']} |"
            )
        lines.append("")
        open(os.path.join(ROOT, "categories", c["id"] + ".md"), "w", encoding="utf-8").write("\n".join(lines))

    tools_dir = os.path.join(ROOT, "tools")
    if os.path.isdir(tools_dir):
        shutil.rmtree(tools_dir)
    os.makedirs(tools_dir)
    for t in tools:
        fn = t["full_name"].replace("/", "__") + ".md"
        p = t["score_parts"]
        lines = [
            f"# {t['full_name']}", "",
            f"- 仓库：{t['url']}",
            f"- 分类：{cat_name[t['category']]}（`{t['category']}`）",
            f"- 一句话：{t['description_zh']}",
            f"- Stars：{t['stars']:,}（{t['verified_at']} 核查）",
            f"- Forks：{t['forks']:,}",
            f"- 最近提交：{t['pushed_at'][:10]}",
            f"- License：{t['license']}",
            f"- 免费级别：{t['free_level']}（{t['free_note']}）",
            f"- 部署：{t['deploy']}",
            f"- 中国可用：{t['china_access']}",
            f"- 适用场景：{t['use_case']}",
            f"- 风险/限制：{t['risk']}",
            f"- 评分：**{t['score']}**（场景 {p['场景匹配']} / 维护 {p['维护活跃']} / "
            f"免费 {p['免费许可']} / 部署 {p['部署可控']} / 合规 {p['数据合规']} / 中国 {p['中国可用']}）",
            f"- 级别：**{t['level']}**",
            f"- 证据：{t['url']} · {t['url']}/releases · {t['url']}/blob/main/LICENSE",
            f"- 备注：{t['description_en']}" if t["description_en"] else "- 备注：—",
            "",
        ]
        open(os.path.join(tools_dir, fn), "w", encoding="utf-8").write("\n".join(lines))

    rejected = os.path.join(ROOT, "rejected.md")
    if not os.path.exists(rejected):
        open(rejected, "w", encoding="utf-8").write(
            "# 淘汰记录\n\n> 豆包每批把淘汰项追加到这里，写清 URL、核查日期、淘汰原因。牛牛复核后保留。\n\n"
            "| 日期 | 仓库/工具 | 原因 | 证据 |\n|---|---|---|---|\n"
            "| 2026-10-30 | — | 种子库暂无淘汰项 | — |\n"
        )

    wb = os.path.expanduser("~/Desktop/宏锐智能助手_v0.2/data")
    os.makedirs(wb, exist_ok=True)
    page = {
        "meta": catalog["meta"],
        "categories": CATEGORIES,
        "tools": tools,
        "repo": "https://github.com/hujianming0910/customer-acquisition-tools",
        "task_file": "/Users/hujianming/Desktop/工控副业工具/_豆包交接/GitHub客户获取工具库_总体方案与豆包任务_20261030.md",
        "readme_url": "https://github.com/hujianming0910/customer-acquisition-tools/blob/main/README.md",
        "tools_url": "https://github.com/hujianming0910/customer-acquisition-tools/blob/main/TOOLS.md",
        "progress": {
            "phase": "种子库已建，待豆包批次01",
            "updated": "2026-10-30",
            "batches": [
                {"id": "01", "name": "核心栈", "status": "待开始", "candidates": 0, "p0": 0},
                {"id": "02", "name": "线索发现", "status": "待开始", "candidates": 0, "p0": 0},
                {"id": "03", "name": "内容/SEO/分析", "status": "待开始", "candidates": 0, "p0": 0},
                {"id": "04", "name": "触达与合规", "status": "待开始", "candidates": 0, "p0": 0},
                {"id": "05", "name": "中国场景/长尾", "status": "待开始", "candidates": 0, "p0": 0},
            ],
        },
    }
    json.dump(page, open(os.path.join(wb, "github_tools.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    print(f"built {len(tools)} tools: P0={catalog['meta']['p0']} P1={catalog['meta']['p1']} P2={catalog['meta']['p2']}")


if __name__ == "__main__":
    build()
