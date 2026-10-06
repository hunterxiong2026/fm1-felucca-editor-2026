/**
 * Felucca / FM-1 参数映射表
 *
 * 基于 DX7 标准 SysEx 格式: F0 43 1n pp qq vv F7
 * 全局参数 (pp=01) 在 Felucca 中有 +2 的地址偏移（社区确认）
 *
 * 所有值范围均为 0-99（DX7 标准），发送时需转为十六进制。
 */

window.__FELUCCA_PARAMS = {

  // ==================== 元数据 ====================
  _meta: {
    sysexHeader: [0xF0, 0x43, 0x10],
    sysexTerminator: 0xF7,
    valueMax: 99,
    globalOffset: 2,  // 全局参数地址偏移
  },

  // ==================== 操作器基地址 ====================
  _opBase: {
    6: 0x00, 5: 0x15, 4: 0x2A,
    3: 0x3F, 2: 0x54, 1: 0x69,
  },

  // ==================== 操作器参数 (pp = 00) ====================
  // 以下参数地址为相对于操作器基地址的偏移

  // --- 包络 (Envelope) ---
  'op.egRate1':       { group: 0x00, offset: 0x00, min: 0, max: 99, desc: '包络 Attack 速度' },
  'op.egRate2':       { group: 0x00, offset: 0x01, min: 0, max: 99, desc: '包络 Decay 1 速度' },
  'op.egRate3':       { group: 0x00, offset: 0x02, min: 0, max: 99, desc: '包络 Decay 2 速度' },
  'op.egRate4':       { group: 0x00, offset: 0x03, min: 0, max: 99, desc: '包络 Release 速度' },
  'op.egLevel1':      { group: 0x00, offset: 0x04, min: 0, max: 99, desc: '包络 Peak 电平' },
  'op.egLevel2':      { group: 0x00, offset: 0x05, min: 0, max: 99, desc: '包络 Decay 1 电平' },
  'op.egLevel3':      { group: 0x00, offset: 0x06, min: 0, max: 99, desc: '包络 Sustain 电平' },
  'op.egLevel4':      { group: 0x00, offset: 0x07, min: 0, max: 99, desc: '包络 Release/Start 电平' },

  // --- 键盘电平缩放 ---
  'op.kbdBreakPoint': { group: 0x00, offset: 0x08, min: 0, max: 99, desc: '缩放断点' },
  'op.kbdLeftDepth':  { group: 0x00, offset: 0x09, min: 0, max: 99, desc: '断点左侧衰减深度' },
  'op.kbdRightDepth': { group: 0x00, offset: 0x0A, min: 0, max: 99, desc: '断点右侧衰减深度' },
  'op.kbdLeftCurve':  { group: 0x00, offset: 0x0B, min: 0, max: 3, desc: '左曲线: 0=-LIN,1=-EXP,2=+EXP,3=+LIN' },
  'op.kbdRightCurve': { group: 0x00, offset: 0x0C, min: 0, max: 3, desc: '右曲线: 0=-LIN,1=-EXP,2=+EXP,3=+LIN' },
  'op.kbdRateScaling': { group: 0x00, offset: 0x0D, min: 0, max: 7, desc: '键跟踪速度修饰' },
  'op.ampModSens':    { group: 0x00, offset: 0x0E, min: 0, max: 3, desc: 'LFO 幅度调制敏感度' },
  'op.velocitySens':  { group: 0x00, offset: 0x0F, min: 0, max: 7, desc: '力度响应深度' },

  // --- 振荡器 ---
  'op.outputLevel':   { group: 0x00, offset: 0x10, min: 0, max: 99, desc: '输出电平' },
  'op.oscMode':       { group: 0x00, offset: 0x11, min: 0, max: 1, desc: '0=频率比率, 1=固定Hz' },
  'op.freqCoarse':    { group: 0x00, offset: 0x12, min: 0, max: 31, desc: '粗调' },
  'op.freqFine':      { group: 0x00, offset: 0x13, min: 0, max: 99, desc: '微调' },
  'op.detune':        { group: 0x00, offset: 0x14, min: 0, max: 14, desc: '失谐 (7=居中)' },

  // ==================== 全局参数 (pp = 01) ====================
  // 注意: Felucca 中全局参数地址有 +2 偏移

  'global.algorithm':     { group: 0x01, offset: 0x00 + 2, min: 0, max: 31, desc: 'FM 算法' },
  'global.feedback':      { group: 0x01, offset: 0x01 + 2, min: 0, max: 7, desc: '反馈量' },
  'global.oscSync':       { group: 0x01, offset: 0x02 + 2, min: 0, max: 1, desc: '振荡器同步' },
  'global.lfoSpeed':      { group: 0x01, offset: 0x03 + 2, min: 0, max: 99, desc: 'LFO 速度' },
  'global.lfoDelay':      { group: 0x01, offset: 0x04 + 2, min: 0, max: 99, desc: 'LFO 延迟' },
  'global.lfoPitchMod':   { group: 0x01, offset: 0x05 + 2, min: 0, max: 99, desc: 'LFO 音高调制深度' },
  'global.lfoAmpMod':     { group: 0x01, offset: 0x06 + 2, min: 0, max: 99, desc: 'LFO 幅度调制深度' },
  'global.lfoWave':       { group: 0x01, offset: 0x07 + 2, min: 0, max: 5, desc: 'LFO 波形' },
  'global.lfoSync':       { group: 0x01, offset: 0x08 + 2, min: 0, max: 1, desc: 'LFO 键同步' },
  'global.pitchEnvRate1': { group: 0x01, offset: 0x09 + 2, min: 0, max: 99, desc: '音高包络 Rate 1' },
  'global.pitchEnvRate2': { group: 0x01, offset: 0x0A + 2, min: 0, max: 99, desc: '音高包络 Rate 2' },
  'global.pitchEnvRate3': { group: 0x01, offset: 0x0B + 2, min: 0, max: 99, desc: '音高包络 Rate 3' },
  'global.pitchEnvRate4': { group: 0x01, offset: 0x0C + 2, min: 0, max: 99, desc: '音高包络 Rate 4' },
  'global.pitchEnvLevel1': { group: 0x01, offset: 0x0D + 2, min: 0, max: 99, desc: '音高包络 Level 1' },
  'global.pitchEnvLevel2': { group: 0x01, offset: 0x0E + 2, min: 0, max: 99, desc: '音高包络 Level 2' },
  'global.pitchEnvLevel3': { group: 0x01, offset: 0x0F + 2, min: 0, max: 99, desc: '音高包络 Level 3' },
  'global.pitchEnvLevel4': { group: 0x01, offset: 0x10 + 2, min: 0, max: 99, desc: '音高包络 Level 4' },
  'global.transpose':      { group: 0x01, offset: 0x11 + 2, min: 0, max: 48, desc: '移调' },

  // ==================== Felucca 扩展效果器 (pp = 02) ====================
  // 以下为 Felucca 扩展参数，地址需对照源码确认（标记为待验证）

  'fx.filterCutoff':  { group: 0x02, offset: 0x00, min: 0, max: 99, desc: '滤波器截止频率 [待验证]' },
  'fx.filterReso':    { group: 0x02, offset: 0x01, min: 0, max: 99, desc: '滤波器共振 [待验证]' },
  'fx.reverbMix':     { group: 0x02, offset: 0x02, min: 0, max: 99, desc: '混响混合比 [待验证]' },
  'fx.delayMix':      { group: 0x02, offset: 0x03, min: 0, max: 99, desc: '延迟混合比 [待验证]' },
  'fx.distortion':    { group: 0x02, offset: 0x04, min: 0, max: 99, desc: '失真量 [待验证]' },
  'fx.chorus':        { group: 0x02, offset: 0x05, min: 0, max: 99, desc: '合唱深度 [待验证]' },
  'fx.phaser':        { group: 0x02, offset: 0x06, min: 0, max: 99, desc: '移相器深度 [待验证]' },
};

// ---- 便捷函数 ----

// 计算操作器参数的实际地址
window.__FELUCCA_PARAMS.getOpAddress = function (op, paramOffset) {
  const base = this._opBase[op];
  if (base === undefined) throw new Error(`无效操作器: ${op} (有效值: 1-6)`);
  return base + paramOffset;
};

// 查找参数定义
window.__FELUCCA_PARAMS.lookup = function (name) {
  const def = this[name];
  if (!def) throw new Error(`未知参数: ${name}`);
  return def;
};

// 列出所有参数名
window.__FELUCCA_PARAMS.listAll = function () {
  return Object.keys(this).filter(k => !k.startsWith('_') && typeof this[k] === 'object' && this[k].group !== undefined);
};