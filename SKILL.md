---
name: felucca-editor
version: 1.3.0
author: hunterxiong2026
license: MIT
description: "通过直连 SysEx（ctypes + winmm）操作 M-VAVE FM-1 的 Felucca 固件，实现音色参数编辑、多轨编曲、项目槽位管理与 SONG 播放链。"
keywords:
  - fm1
  - felucca
  - m-vave
  - sysex
  - winmm
  - ctypes
  - synthesizer
  - music-production
  - arrangement
categories:
  - music
  - automation
  - hardware-integration
triggers:
  - "用 Felucca 编一段"
  - "调整 FM-1 音色"
  - "写一段鼓点/贝斯/旋律"
  - "存到槽位"
  - "播放槽位 A/B"
requirements:
  - name: m-vave-fm1
    type: hardware
    optional: false
  - name: felucca-firmware
    type: firmware
    version: "1.5"
    optional: false
  - name: python
    type: runtime
    version: "3.10+"
    optional: false
  - name: windows
    type: platform
    optional: false
platforms:
  - windows
---

# Felucca Editor Skill

## 概述
通过直连 SysEx 协议操控 FM-1 上的 Felucca 固件。

## 何时使用
- 用户要求写一段编曲（旋律/贝斯/和声/鼓）
- 用户要求修改音色参数（滤波器、包络、LFO、琶音、调制矩阵等）
- 用户要求存/读槽位、播放 SONG 链
- 用户要求验证设备状态（dump 当前工作区）

## 前置条件
1. **独立 venv**：`scripts/venv/`，绝不装任何包进系统
2. **设备空闲**：直连前必须关闭浏览器/任何 Web MIDI 会话（设备输入独占）
3. **设备名**：动态匹配关键字含 `felucca`（可用 `FELUCCA_MIDI_NAME` 环境变量指定）
4. **固件版本**：FELUCCA **1.5**（111 轨道参数 / 27 全局参数）

## 脚本清单

| 脚本 | 作用 |
|---|---|
| `felucca_link.py` | 直连核心库（动态设备匹配 / 收发 / INFO·DESC·STEP·SONG 解析） |
| `felucca_cli.py` | 命令行工具 |
| `felucca_arrange.py` | 单槽一键编曲 |
| `felucca_arrange_ab.py` | 双槽链编曲 |
| `play_slot.py` / `play_chain.py` | 仅播放脚本 |

## 使用流程
```
用户描述需求
    ↓
AI 设计编曲方案
    ↓
调用 felucca_arrange.py 写入设备
    ↓
PROJECT save（显式保存）
    ↓
SONG 播放
    ↓
实际听声验收
```

## 参考（生成前必读）
- `reference/protocol.md`：帧格式、命令表、STEP/SONG 布局、INFO 解析、直连坑、设备名匹配
- `reference/params.md`：111 轨道参数 + 27 全局参数 + 枚举
- `reference/sysx-map.md`：DX7 标准参数映射
- `reference/arrangement-metrics.md`：编曲质量指标
- `examples/arrangement-recipes.md`：编曲配方

## 用户硬约束
1. **独立 venv，绝不装任何包进系统**
2. 直连前关闭浏览器 / Web MIDI 会话
3. 播放验收以实际听声为准
4. 修改后直接改文件与设备，不输出提示词正文
5. 回复先给一句话总结

## 已知限制
- 仅支持 Windows（依赖 winmm.dll）
- 多行链 `repeat>1` 不稳（单遍链稳定）
- Felucca 固件为 Beta，刷入有变砖风险