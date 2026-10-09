"""
felucca_link.py — FM-1 / Felucca 直连 SysEx 核心库（已按 1.1.5.1 实测校准）

零第三方依赖，仅用 ctypes 直调 Windows winmm.dll。
协议帧：F0 7D 46 4C <cmd & 0x7F> <args...> F7
固件：FELUCCA 1.1.5.1（实测：14 引擎 / 64 步 / 4 轨 / 99 轨道参数）
      （1.0.2 为 91 参数，已过时）

⚠️ 与 SLOOP 的关键差异：
  - 命令 33 = SONG（SLOOP 是 DRUM_STEP）
  - 写步带 chance 字节（SLOOP 无）
  - 8 鼓位用 hit/acc 位掩码（SLOOP 用 16 lane 掩码）
  - 1.1.5.1 读步回复尾部多 1 字节（忽略即可）
"""

import ctypes
import time
from ctypes import wintypes

# ---------- winmm 常量 ----------
CALLBACK_FUNCTION = 0x00030000
MIM_LONGDATA = 0x3C4        # ⚠️ 不是 0x3C6
MHDR_DONE = 0x00000001

# ---------- 命令枚举 ----------
CMD_INFO = 1
CMD_GET = 2
CMD_SET = 3
CMD_DESC = 5
CMD_STEP_GET = 6
CMD_STEP_SET = 7
CMD_PRESET = 8
CMD_PROJECT = 9
CMD_WATCH = 22
CMD_TRACK = 27
CMD_TRACK_STEP = 30
CMD_TRACK_PARAM = 31
CMD_SONG = 33            # ⚠️ Felucca：SONG 播放链（SLOOP 是 DRUM_STEP）

HDR = [0x7D, 0x46, 0x4C]

# ---------- 轨道参数 ID（1.1.5.1：99 个，0-98） ----------
P_LVL, P_ATK, P_DEC, P_SUS, P_REL = 0, 1, 2, 3, 4
P_FLT, P_PIT, P_SHP, P_FX = 5, 6, 7, 8
P_LFO1_RATE, P_LFO1_WAVE, P_LFO1_PHS, P_LFO1_FADE = 9, 10, 11, 12
P_LFO2_PIT, P_LFO2_FLT, P_LFO2_SHP, P_LFO2_AMP = 13, 14, 15, 16
P_ARP_MODE, P_ARP_RATE, P_ARP_OCT, P_ARP_GATE = 17, 18, 19, 20
P_ARP_SWG, P_ARP_PROB, P_ARP_HOLD, P_ARP_ORD = 21, 22, 23, 24
P_SCL_ROOT, P_SCL, P_QNT, P_TRN = 25, 26, 27, 28
P_LEN, P_DIV, P_SWG, P_GATE = 29, 30, 31, 32
P_DST, P_CHO, P_DLY, P_REV = 33, 34, 35, 36
P_VCE, P_GLD, P_PAN, P_MUTE = 37, 38, 39, 40
P_GLMOD, P_PRIO, P_ALLOC, P_DTUNE, P_SLCR = 41, 42, 43, 44, 45
P_PAT, P_RATE, P_DEPTH = 46, 47, 48
# 调制矩阵（4 组 SRC×DST×AMT）
P_SRC1, P_DST1, P_AMT1 = 49, 50, 51
P_SRC2, P_DST2, P_AMT2 = 52, 53, 54
P_SRC3, P_DST3, P_AMT3 = 55, 56, 57
P_SRC4, P_DST4, P_AMT4 = 58, 59, 60
# 4×ENV（每组 ATK/DEC/SUS/REL/LVL）
P_ENV1_ATK, P_ENV1_DEC, P_ENV1_SUS, P_ENV1_REL, P_ENV1_LVL = 61, 62, 63, 64, 65
P_ENV2_ATK, P_ENV2_DEC, P_ENV2_SUS, P_ENV2_REL, P_ENV2_LVL = 66, 67, 68, 69, 70
P_ENV3_ATK, P_ENV3_DEC, P_ENV3_SUS, P_ENV3_REL, P_ENV3_LVL = 71, 72, 73, 74, 75
P_ENV4_ATK, P_ENV4_DEC, P_ENV4_SUS, P_ENV4_REL, P_ENV4_LVL = 76, 77, 78, 79, 80
# 和弦模式
P_CHRD, P_VOIC = 81, 82
# 鼓 8 件套音量（1.1.5.1 新增，原 1.0.2 的 ANALOG EDIT 位置）
P_DRUM_KICK, P_DRUM_SNARE, P_DRUM_CLAP, P_DRUM_HATCL = 83, 84, 85, 86
P_DRUM_HATOP, P_DRUM_TOM, P_DRUM_RIM, P_DRUM_BELL = 87, 88, 89, 90
# ANALOG EDIT（1.0.2 是 83-90，1.1.5.1 后移 +8）
P_A_WAVE, P_A_DTN, P_A_MIX, P_A_NOIS = 91, 92, 93, 94
P_A_CUT, P_A_RES, P_A_DRV, P_A_KTR = 95, 96, 97, 98

# ---------- 全局参数 ID（27 个，0-24） ----------
G_BPM, G_SWG, G_CLK, G_TUNE, G_TIME = 0, 1, 2, 3, 4
G_DLY_FDBK, G_DLY_COLR, G_DLY_MIX, G_DLY_SIZE, G_DLY_DAMP = 5, 6, 7, 8, 9
G_CRT, G_CDP, G_MIDI, G_SYNC, G_ROUT = 10, 11, 12, 13, 14
G_CPU, G_SLOT, G_NAME, G_LOAD, G_SAVE = 15, 16, 17, 18, 19
G_ENG, G_SET, G_CLRSQ, G_INIT, G_TYPE = 20, 21, 22, 23, 24

# ---------- 枚举 ----------
ENGINES = {
    'ANALOG': 0, '': 1, 'PHASE': 2, 'LOFI': 3, 'SAMPLE': 4, 'VOICE': 5,
    'TRIO': 6, 'WHEEL': 7, 'GRAIN': 8, 'PHYS': 9, 'DRUM': 10,
    'NOISE': 11, 'FM6': 12, 'SLICE': 13,
}
ENGINE_NAMES = {v: k for k, v in ENGINES.items()}

DIVS = {'1/4': 0, '1/8': 1, '1/16': 2, '1/32': 3,
        '8T': 4, '16T': 5, '1/2': 6, '1/1': 7}
DIV_NAMES = {v: k for k, v in DIVS.items()}

TIME_NOTE, TIME_TIE, TIME_REST = 0, 1, 2

# 8 鼓位 lane 对应的 GM 音
DRUM_LANES = {
    0: ('KICK',  36),
    1: ('SNARE', 38),
    2: ('CLAP',  39),
    3: ('HATCL', 42),
    4: ('HATOP', 46),
    5: ('TOM',   45),
    6: ('RIM',   37),
    7: ('BELL',  56),
}
LANE_BY_NAME = {name: idx for idx, (name, _) in DRUM_LANES.items()}

# ANALOG 预设（1.1.5.1，pcount=99）
ANALOG_PRESETS = {
    'SOFT PAD': 1, 'SINE KEY': 5, 'SUB BASS': 7, 'BRASS': 9,
}

# ---------- winmm 结构体 ----------
class MIDIHDR(ctypes.Structure):
    """⚠️ 与 sloop_link.py 逐字段一致（实测这是唯一能稳定收全帧的声明）。
    lpData 用 c_void_p、dwUser/reserved 用 c_ulonglong，共 88B。"""
    _fields_ = [
        ("lpData", ctypes.c_void_p),
        ("dwBufferLength", wintypes.DWORD),
        ("dwBytesRecorded", wintypes.DWORD),
        ("dwUser", ctypes.c_ulonglong),
        ("dwFlags", wintypes.DWORD),
        ("lpNext", ctypes.c_void_p),
        ("reserved", ctypes.c_ulonglong),
        ("dwOffset", wintypes.DWORD),
        ("dwReserved", ctypes.c_void_p * 4),
    ]

class MIDIINCAPS(ctypes.Structure):
    _fields_ = [
        ("wMid", wintypes.WORD), ("wPid", wintypes.WORD),
        ("vDriverVersion", wintypes.UINT),
        ("szPname", wintypes.WCHAR * 32),
        ("dwSupport", wintypes.DWORD),
    ]

class MIDIOUTCAPS(ctypes.Structure):
    _fields_ = [
        ("wMid", wintypes.WORD), ("wPid", wintypes.WORD),
        ("vDriverVersion", wintypes.UINT),
        ("szPname", wintypes.WCHAR * 32),
        ("wTechnology", wintypes.WORD),
        ("wVoices", wintypes.WORD), ("wNotes", wintypes.WORD),
        ("wChannelMask", wintypes.WORD),
        ("dwSupport", wintypes.DWORD),
    ]

# ---------- winmm 绑定（argtypes 必须显式声明）----------
winmm = ctypes.WinDLL('winmm')

winmm.midiInGetNumDevs.restype = wintypes.UINT
winmm.midiInGetDevCapsW.argtypes = [wintypes.UINT, ctypes.POINTER(MIDIINCAPS), wintypes.UINT]
winmm.midiInGetDevCapsW.restype = wintypes.UINT
winmm.midiInOpen.argtypes = [ctypes.POINTER(wintypes.HANDLE), wintypes.UINT,
                             ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD]
winmm.midiInOpen.restype = wintypes.UINT
winmm.midiInClose.argtypes = [wintypes.HANDLE]
winmm.midiInStart.argtypes = [wintypes.HANDLE]
winmm.midiInStop.argtypes = [wintypes.HANDLE]
winmm.midiInReset.argtypes = [wintypes.HANDLE]
winmm.midiInPrepareHeader.argtypes = [wintypes.HANDLE, ctypes.POINTER(MIDIHDR), wintypes.UINT]
winmm.midiInPrepareHeader.restype = wintypes.UINT
winmm.midiInAddBuffer.argtypes = [wintypes.HANDLE, ctypes.POINTER(MIDIHDR), wintypes.UINT]
winmm.midiInAddBuffer.restype = wintypes.UINT
winmm.midiInUnprepareHeader.argtypes = [wintypes.HANDLE, ctypes.POINTER(MIDIHDR), wintypes.UINT]

winmm.midiOutGetNumDevs.restype = wintypes.UINT
winmm.midiOutGetDevCapsW.argtypes = [wintypes.UINT, ctypes.POINTER(MIDIOUTCAPS), wintypes.UINT]
winmm.midiOutGetDevCapsW.restype = wintypes.UINT
winmm.midiOutOpen.argtypes = [ctypes.POINTER(wintypes.HANDLE), wintypes.UINT,
                              ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD]
winmm.midiOutOpen.restype = wintypes.UINT
winmm.midiOutClose.argtypes = [wintypes.HANDLE]
winmm.midiOutPrepareHeader.argtypes = [wintypes.HANDLE, ctypes.POINTER(MIDIHDR), wintypes.UINT]
winmm.midiOutPrepareHeader.restype = wintypes.UINT
winmm.midiOutLongMsg.argtypes = [wintypes.HANDLE, ctypes.POINTER(MIDIHDR), wintypes.UINT]
winmm.midiOutLongMsg.restype = wintypes.UINT
winmm.midiOutUnprepareHeader.argtypes = [wintypes.HANDLE, ctypes.POINTER(MIDIHDR), wintypes.UINT]

# ---------- 设备枚举 ----------
def list_inputs():
    n = winmm.midiInGetNumDevs()
    out = []
    for i in range(n):
        caps = MIDIINCAPS()
        if winmm.midiInGetDevCapsW(i, ctypes.byref(caps), ctypes.sizeof(caps)) == 0:
            out.append((i, caps.szPname))
    return out

def list_outputs():
    n = winmm.midiOutGetNumDevs()
    out = []
    for i in range(n):
        caps = MIDIOUTCAPS()
        if winmm.midiOutGetDevCapsW(i, ctypes.byref(caps), ctypes.sizeof(caps)) == 0:
            out.append((i, caps.szPname))
    return out

def find_felucca():
    in_idx = next((i for i, name in list_inputs() if 'felucca' in name.lower()), None)
    out_idx = next((i for i, name in list_outputs() if 'felucca' in name.lower()), None)
    return in_idx, out_idx

# ---------- 编码 ----------
def v14enc(v):
    x = v + 8192
    return [x & 0x7F, (x >> 7) & 0x7F]

def v14dec(lo, hi):
    return (lo + (hi << 7)) - 8192

def hitsEnc(hit, acc):
    """8 鼓位 lane 编码 → [hit & 0x7F, acc & 0x7F, hi]"""
    hi = ((hit >> 7) & 1) | (((acc >> 7) & 1) << 1)
    return [hit & 0x7F, acc & 0x7F, hi]

def hitsDec(h, c, x):
    """解码 hit/acc。acc 必须 ⊆ hit。"""
    hit = h | ((x & 1) << 7)
    acc = (c | ((x & 2) << 6)) & hit
    return hit, acc

def build_frame(cmd, args):
    return bytes([0xF0] + HDR + [(cmd & 0x7F)] + list(args) + [0xF7])

# ---------- 连接 ----------
class FeluccaLink:
    def __init__(self):
        self.h_in = None
        self.h_out = None
        self._rx_queue = []
        self._rx_acc = bytearray()   # 累积未切帧的输入字节（按 F7 切完整帧）
        self._in_buf = None
        self._in_hdr = None
        self._cb_ref = None

    def open(self):
        in_idx, out_idx = find_felucca()
        if in_idx is None or out_idx is None:
            raise RuntimeError('未找到 Felucca MIDI 设备。请确认 FM-1 已连接，且浏览器/Web MIDI 已关闭。')

        # ---- 输入 ----
        h = wintypes.HANDLE()
        self._in_buf = ctypes.create_string_buffer(8192)
        # ⚠️ 位置式构造（实测稳定收全帧的关键）
        self._in_hdr = MIDIHDR(ctypes.addressof(self._in_buf), 8192, 0, 0, 0, 0, 0, 0,
                               (ctypes.c_void_p * 4)())

        # ⚠️ winmm 回调必须是 5 参数
        # void CALLBACK MidiInProc(HMIDIIN, UINT, DWORD_PTR, DWORD_PTR, DWORD_PTR)
        CB = ctypes.WINFUNCTYPE(None,
                                wintypes.HANDLE,     # hMidiIn
                                wintypes.UINT,       # wMsg
                                ctypes.c_void_p,     # dwInstance
                                ctypes.c_void_p,     # dwParam1 (MIDIHDR*)
                                ctypes.c_void_p)     # dwParam2

        def _cb(hMidiIn, wMsg, dwInstance, dwParam1, dwParam2):
            if wMsg == MIM_LONGDATA:
                hdr_ptr = ctypes.cast(dwParam1, ctypes.POINTER(MIDIHDR))
                hdr = hdr_ptr.contents
                if hdr.dwBytesRecorded > 0:
                    data = ctypes.string_at(hdr.lpData, hdr.dwBytesRecorded)
                    # ⚠️ 必须累积并按 F7 切完整帧：设备会连续推多帧
                    # （如选轨后的 TRACK 通知 rc=27 + 真正的回复帧）
                    self._rx_acc += data
                    while True:
                        i = self._rx_acc.find(bytes([0xF7]))
                        if i < 0:
                            break
                        frame = bytes(self._rx_acc[:i + 1])
                        del self._rx_acc[:i + 1]
                        self._rx_queue.append(frame)
                winmm.midiInAddBuffer(self.h_in, hdr_ptr, ctypes.sizeof(MIDIHDR))
        self._cb_ref = CB(_cb)

        rc = winmm.midiInOpen(ctypes.byref(h), in_idx,
                              ctypes.cast(self._cb_ref, ctypes.c_void_p), None, CALLBACK_FUNCTION)
        if rc != 0:
            raise RuntimeError(f'midiInOpen 失败: {rc}')
        self.h_in = h
        winmm.midiInPrepareHeader(self.h_in, ctypes.byref(self._in_hdr), ctypes.sizeof(MIDIHDR))
        winmm.midiInAddBuffer(self.h_in, ctypes.byref(self._in_hdr), ctypes.sizeof(MIDIHDR))
        winmm.midiInStart(self.h_in)

        # ---- 输出 ----
        h = wintypes.HANDLE()
        rc = winmm.midiOutOpen(ctypes.byref(h), out_idx, None, None, 0)
        if rc != 0:
            winmm.midiInClose(self.h_in)
            raise RuntimeError(f'midiOutOpen 失败: {rc}')
        self.h_out = h
        return self

    def close(self):
        """⚠️ 不要调用 midiInReset：在有 pending buffer 时会与回调线程死锁（实测必现）。
        与 sloop_link.py 一致：Stop → UnprepareHeader → Close。"""
        if self.h_in:
            try:
                winmm.midiInStop(self.h_in)
            except Exception:
                pass
            try:
                winmm.midiInUnprepareHeader(self.h_in, ctypes.byref(self._in_hdr), ctypes.sizeof(MIDIHDR))
            except Exception:
                pass
            winmm.midiInClose(self.h_in)
            self.h_in = None
        if self.h_out:
            winmm.midiOutClose(self.h_out)
            self.h_out = None

    def send(self, frame: bytes):
        buf = ctypes.create_string_buffer(frame)  # ⚠️ 带 NUL
        hdr = MIDIHDR(ctypes.addressof(buf), len(frame), 0, 0, 0, 0, 0, 0,
                      (ctypes.c_void_p * 4)())
        winmm.midiOutPrepareHeader(self.h_out, ctypes.byref(hdr), ctypes.sizeof(MIDIHDR))
        winmm.midiOutLongMsg(self.h_out, ctypes.byref(hdr), ctypes.sizeof(MIDIHDR))
        for _ in range(400):
            if hdr.dwFlags & MHDR_DONE:
                break
            time.sleep(0.005)
        winmm.midiOutUnprepareHeader(self.h_out, ctypes.byref(hdr), ctypes.sizeof(MIDIHDR))

    def send_cmd(self, cmd, args):
        self.send(build_frame(cmd, args))

    def _poll_rx(self, timeout=1.0):
        end = time.time() + timeout
        while time.time() < end:
            if self._rx_queue:
                return self._rx_queue.pop(0)
            time.sleep(0.01)
        return None

    def request(self, cmd, args, timeout=2.0):
        """发命令并等 rc==cmd 的完整回复帧。跳过其它推送帧（如选轨后的 TRACK 通知 rc=27）。"""
        self._rx_queue.clear()
        self.send_cmd(cmd, args)
        end = time.time() + timeout
        while time.time() < end:
            fr = self._poll_rx(max(0.02, min(0.2, end - time.time())))
            if fr is None:
                continue
            if len(fr) < 6 or fr[0] != 0xF0 or fr[-1] != 0xF7 or fr[1:4] != bytes(HDR):
                continue
            if fr[4] == (cmd & 0x7F):
                return fr
        return None

    # ---- 高层 API ----
    def info(self):
        """解析 INFO 回复。Felucca 1.1.5.1 实测：
        version='FELUCCA 1.1.5.1', nengines=14, pcount=99, gcount=27,
        nstep=64, pe0=91, ntrk=4, trailer=[16,85,1,9,...]（30B）

        结构: version(\\0串) nengines(1B) pcount(1B) gcount(1B)
              nstep(1B) pe0(1B) engines×nengines(\\0串) ntrk(1B) trailer[...]

        trailer[0]===16 → chainRows=16
        trailer[0]==16 && trailer[1]==0x55 && trailer[2]==1 → uiCaps = trailer[3] & 15
        """
        r = self.request(CMD_INFO, [])
        if not r or len(r) < 6:
            return None
        body = list(r[5:-1])
        try:
            z = body.index(0x00)
        except ValueError:
            return {'raw': body}
        version = bytes(body[:z]).decode('ascii', errors='replace')
        p = body[z+1:]
        out = {'version': version}
        if len(p) >= 5:
            out['nengines'] = p[0]
            out['pcount']   = p[1]
            out['gcount']   = p[2]
            out['nstep']    = p[3]
            out['pe0']      = p[4]
        # 跳过 engines 串（nengines 个 \0 结尾串）
        rest = p[5:]
        i = 0
        want = out.get('nengines', 0)
        for _ in range(want):
            try:
                zz = rest.index(0x00, i)
            except ValueError:
                break
            i = zz + 1
        # ntrk：独立 1 字节
        if i < len(rest):
            out['ntrk'] = rest[i]
            i += 1
        trailer = rest[i:]
        out['trailer_raw'] = list(trailer)
        if trailer:
            out['chainRows'] = 16 if trailer[0] == 16 else 0
            if (trailer[0] == 16 and len(trailer) >= 4
                    and trailer[1] == 0x55 and trailer[2] == 1):
                out['uiCaps'] = trailer[3] & 15
            else:
                out['uiCaps'] = None
        else:
            out['chainRows'] = 0
            out['uiCaps'] = None
        return out

    def desc(self, scope, pid):
        r = self.request(CMD_DESC, [scope, pid])
        if not r or len(r) < 11:
            return None
        b = list(r[5:-1])
        if len(b) < 11:
            return None
        scope_, id_, fmt = b[0], b[1], b[2]
        mn = v14dec(b[3], b[4])
        mx = v14dec(b[5], b[6])
        dv = v14dec(b[7], b[8])
        i = 9
        try:
            z1 = b.index(0x00, i)
            label = bytes(b[i:z1]).decode('ascii', 'replace')
            i = z1 + 1
            z2 = b.index(0x00, i)
            unit = bytes(b[i:z2]).decode('ascii', 'replace')
        except ValueError:
            label, unit = '', ''
        return {'scope': scope_, 'id': id_, 'fmt': fmt,
                'min': mn, 'max': mx, 'def': dv,
                'label': label, 'unit': unit}

    def select_track(self, track):
        self.send_cmd(CMD_TRACK, [track])

    def preset(self, engine, preset):
        self.send_cmd(CMD_PRESET, [engine, preset])

    def save_slot(self, slot):
        self.send_cmd(CMD_PROJECT, [1, slot])

    def load_slot(self, slot):
        self.send_cmd(CMD_PROJECT, [0, slot])

    def query_slot(self, slot):
        r = self.request(CMD_PROJECT, [2, slot])
        if not r or len(r) < 8:
            return None
        b = list(r[5:-1])
        return {'op': b[0], 'slot': b[1], 'used': b[2]}

    def track_param(self, track, pid, value=None):
        if value is None:
            r = self.request(CMD_TRACK_PARAM, [track, pid])
            if not r or len(r) < 8:
                return None
            b = list(r[5:-1])
            return v14dec(b[2], b[3])
        self.send_cmd(CMD_TRACK_PARAM, [track, pid] + v14enc(value))

    def set_global(self, pid, value):
        self.send_cmd(CMD_SET, [1, pid] + v14enc(value))

    # ---- 步进 ----
    def write_step(self, track, step, notes, time_mode=TIME_NOTE,
                   velocity=100, flags=0, chance=100, hit=0, acc=0):
        """
        写步（Felucca 带 chance）：
          [tr, i, n, note0..3, time, flags, vel, hit, acc, hi, chance]
        notes: MIDI 音高列表，最多 4 个。
        time_mode: 0=NOTE 1=TIE 2=REST
        hit/acc: 8 鼓位 lane 掩码（非鼓轨 = 0）
        """
        n = min(len(notes), 4)
        nb = [0] * 4
        for i, p in enumerate(notes[:4]):
            nb[i] = int(p)
        he = hitsEnc(hit, acc)
        args = [track, step, n] + nb + [time_mode, flags, velocity] + he + [chance]
        self.send_cmd(CMD_TRACK_STEP, args)

    def read_step(self, track, step):
        """
        读步。回复（v1.1.5.1，14B）：
          [i, n, note0..3, time, flags, vel, hit, acc, hi, chance, extra?]
        ⚠️ v1.1.5.1 尾部多 1 字节（实测 = 1），忽略即可。
        """
        self.select_track(track)
        time.sleep(0.08)
        r = self.request(CMD_STEP_GET, [step])
        if not r or len(r) < 6:
            return None
        b = list(r[5:-1])
        if len(b) < 9:
            return None
        hit, acc = (0, 0)
        if len(b) > 11:
            hit, acc = hitsDec(b[9], b[10], b[11])
        return {
            'i': b[0], 'n': b[1],
            'notes': b[2:6],
            'time': b[6], 'flags': b[7], 'vel': b[8],
            'hit': hit, 'acc': acc,
            'chance': b[12] if len(b) > 12 else 100,
            'extra': b[13] if len(b) > 13 else None,   # v1.1.5.1 新增尾字节
            'raw': b,
        }

    # ---- SONG 播放 ----
    def play_song(self, rows):
        """
        rows: [(slot, repeat), ...]
        发送 op=1 设行 + op=2 播放。
        ⚠️ 只发 op=1 是"配置行"，不出声！必须再发 op=2 才播放。
        """
        args = [1, len(rows)]
        for slot, rep in rows:
            args += [slot, rep]
        self.send_cmd(CMD_SONG, args)
        time.sleep(0.2)
        self.send_cmd(CMD_SONG, [2])

    def stop_song(self):
        self.send_cmd(CMD_SONG, [3])

    def query_song(self):
        r = self.request(CMD_SONG, [0])
        if not r or len(r) < 8:
            return None
        b = list(r[5:-1])
        return {'op': b[0], 'rc': b[1], 'count': b[2], 'playing': b[3],
                'row': b[4], 'remaining': b[5], 'raw': b}