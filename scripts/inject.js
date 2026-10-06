/**
 * Felucca Web Editor 注入脚本
 *
 * 通过 Web MIDI API 与 FM-1 硬件通信。
 * SysEx 格式: F0 43 1n pp qq vv F7
 *   - F0: SysEx 开始
 *   - 43: Yamaha 厂商 ID (FM-1 兼容 DX7 标准)
 *   - 1n: 子状态 + MIDI 通道 (n = 通道 - 1, 默认 Channel 1 → 0x10)
 *   - pp: 参数组 (00 = 操作器, 01 = 全局)
 *   - qq: 参数地址
 *   - vv: 值 (十六进制, 0x00 - 0x63)
 *   - F7: SysEx 结束
 *
 * 来源: Elektronauts 社区确认，Felucca 沿用官方 FM-1 的 DX7 SysEx 格式。
 * 参考: https://www.elektronauts.com/t/m-vave-fm-1/252170
 */

(function () {
  if (window.__felucca) return;

  let midiAccess = null;
  let output = null;
  let input = null;
  const listeners = [];

  // ---- SysEx 头部 ----
  // F0 + Yamaha ID (0x43) + Channel 1 (0x10)
  // 如需切换 MIDI 通道，修改第三个字节: Channel 2 → 0x11, Channel 3 → 0x12, ...
  const SYSEX_HEADER = [0xF0, 0x43, 0x10];
  const SYSEX_TERMINATOR = 0xF7;

  // ---- 初始化 ----
  async function init() {
    midiAccess = await navigator.requestMIDIAccess({ sysex: true });
    const outs = [...midiAccess.outputs.values()];
    const ins = [...midiAccess.inputs.values()];

    output = outs.find(p => /fm-?1|m-?vave|felucca/i.test(p.name)) || outs[0];
    input = ins.find(p => /fm-?1|m-?vave|felucca/i.test(p.name)) || ins[0];

    if (input) {
      input.onmidimessage = (msg) => {
        listeners.forEach(fn => fn(msg.data));
      };
    }
    return { output: output?.name, input: input?.name };
  }

  function listPorts() {
    return {
      outputs: [...(midiAccess?.outputs.values() ?? [])].map(p => p.name),
      inputs: [...(midiAccess?.inputs.values() ?? [])].map(p => p.name),
    };
  }

  // ---- SysEx 发送 ----
  function sendSysEx(bytes) {
    if (!output) throw new Error('MIDI 输出未初始化');
    const msg = [...SYSEX_HEADER, ...bytes, SYSEX_TERMINATOR];
    output.send(msg);
  }

  // ---- 参数设置 ----
  // 根据 params.js 中的定义发送 SysEx
  function setParam(name, value) {
    const def = window.__FELUCCA_PARAMS?.[name];
    if (!def) throw new Error(`未知参数: ${name}`);

    // 将值归一化到 DX7 的 0-99 范围，再转为十六进制
    const normalized = Math.round(
      Math.max(0, Math.min(99, ((value - def.min) / (def.max - def.min)) * 99))
    );
    const hexValue = normalized.toString(16).toUpperCase().padStart(2, '0');

    sendSysEx([def.group, def.offset, parseInt(hexValue, 16)]);
  }

  // ---- 实时演奏 ----
  function note(pitch, velocity = 100, durationMs = 300, channel = 0) {
    if (!output) throw new Error('MIDI 输出未初始化');
    const status = 0x90 | channel;
    output.send([status, pitch, velocity]);
    setTimeout(() => output.send([status, pitch, 0]), durationMs);
  }

  // ---- 播放乐句 ----
  function phrase(events) {
    return Promise.all(
      events.map(ev => new Promise(res => {
        setTimeout(() => {
          note(ev.pitch, ev.vel ?? 100, ev.dur ?? 200, ev.ch ?? 0);
          res();
        }, ev.t);
      }))
    );
  }

  // ---- 监听 ----
  function onMessage(fn) { listeners.push(fn); }

  // ---- 保存到槽位 ----
  // Felucca 保存通常通过 UI 完成，或发送完整的音色 dump SysEx
  // 完整 dump 格式为 4104 字节的 DX7 标准音色数据
  function saveToSlot(slot, name) {
    // 简化实现：提示用户通过 UI 保存
    console.warn('保存操作请通过 Web Editor UI 完成，或发送完整 DX7 dump SysEx');
    throw new Error('保存命令需发送完整的 4104 字节 DX7 dump，请通过 UI 操作');
  }

  // ---- 加载预设 ----
  function loadPreset(presetData) {
    if (!Array.isArray(presetData)) {
      throw new Error('预设数据必须为字节数组');
    }
    // DX7 完整音色 dump 为 4104 字节
    if (presetData.length === 4104) {
      output.send(presetData);
    } else {
      throw new Error(`无效的预设长度: ${presetData.length}，期望 4104 字节`);
    }
  }

  window.__felucca = {
    init, listPorts, setParam, note, phrase, onMessage,
    sendSysEx, saveToSlot, loadPreset,
    _state: () => ({ output: output?.name, input: input?.name }),
    _header: () => [...SYSEX_HEADER],
  };

  return 'felucca injected';
})();