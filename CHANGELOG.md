\# Changelog



本项目所有显著变更均记录于此。

格式基于 \[Keep a Changelog](https://keepachangelog.com/)，

版本号遵循 \[Semantic Versioning](https://semver.org/)。



\## \[Unreleased]



\### 计划

\- \[ ] MIDI 文件导出（`J:\\MyMusic\\midi`）

\- \[ ] 多行链 `repeat>1` 稳定性修复

\- \[ ] `STEP\_GET` 参数布局重验

\- \[ ] 多引擎（ANALOG/PHASE/LOFI 等）参数 SysEx 覆盖

\- \[ ] macOS 支持（CoreMIDI）



\---



\## \[1.0.0] - 2026-10-06



\### 新增

\- \*\*直连 SysEx 方案\*\*（ctypes + winmm.dll），替代已退役的 Web MIDI / CDP 方案

\- `scripts/felucca\_link.py`：直连核心库

&#x20; - 设备枚举（自动识别 `Felucca` 输入/输出端口）

&#x20; - 帧收发（`F0 7D 46 4C <cmd> <args...> F7`）

&#x20; - v14 编解码、hit/acc 位掩码编解码

&#x20; - INFO / DESC / STEP / TRACK\_PARAM / PROJECT / SONG 全部命令

\- `scripts/felucca\_cli.py`：命令行工具（11 个子命令）

\- `scripts/felucca\_arrange.py`：单槽一键编曲（读 JSON → 写 4 轨 → 存槽 → 播放）

\- `scripts/felucca\_arrange\_ab.py`：双槽链一键编曲

\- `scripts/play\_slot.py` / `play\_chain.py`：仅播放脚本

\- `SKILL.md`：入口文档，含完整协议、参数 ID、流程

\- `reference/sysx-map.md`：DX7 标准参数映射

\- `examples/arrangement-recipes.md`：编曲配方（爵士 / 布鲁斯 / 雨后庭院）



\### 修复（相对开发期版本）

\- \*\*INFO 解析修正\*\*：`ntrk` 是解析流中独立 1 字节，不在 trailer 数组内

\- \*\*INFO chainRows 判定\*\*：`trailer\[0] === 16`，不再用模糊的 `0x10 in trailer`

\- \*\*INFO uiCaps 判定\*\*：`trailer\[0]==16 \&\& trailer\[1]==0x55 \&\& trailer\[2]==1 → trailer\[3] \& 15`

\- \*\*STEP\_GET 请求格式\*\*：`\[6, i]` 不是 `\[6, tr, i]`（多带 tr 会 NO REPLY）

\- \*\*winmm 三坑\*\*：MIDIHDR 8 字节指针 / `MIM\_LONGDATA=0x3C4` / argtypes 显式声明

\- \*\*v14 编码\*\*：低 7 位在前，`v14dec(lo, hi) = (lo + (hi << 7)) - 8192`



\### 变更

\- \*\*架构\*\*：Web MIDI 方案退役 → 直连 SysEx 成为唯一路径

&#x20; - 速度对比：整首编曲从 10-20 分钟 → 16-45 秒

&#x20; - 单步 RTT 从 0.9s → 0.12s

\- \*\*文档结构\*\*：SKILL.md 精简入口 + reference/ 详参 + examples/ 配方



\### 已知限制

\- 仅支持 Windows

\- 多行链 `repeat>1` 不稳

\- `STEP\_GET` 参数布局在部分固件上需重验

\- Felucca 固件为 Beta，有变砖风险

