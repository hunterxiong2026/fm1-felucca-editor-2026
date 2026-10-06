"""
felucca_arrange.py — 读取 arrangement.json，写入 4 轨、设 BPM、存槽、播放。

用法:
    python felucca_arrange.py <slot> <bpm> <repeat>

arrangement.json 结构:
{
  "tracks": [
    {
      "engine": "ANALOG",
      "preset": 9,
      "params": {"LEN": 32, "DIV": 1, "SWG": 60, "GATE": 79, "ATK": 20, "REL": 60, "FLT": 80},
      "steps": [
        {"i": 0, "notes": [60], "time": 0, "vel": 100},
        {"i": 1, "notes": [], "time": 1},
        ...
      ]
    },
    ... 共 4 轨
  ]
}
"""

import json
import sys
import time
from felucca_link import (
    FeluccaLink, ENGINES, DIVS,
    TIME_NOTE, TIME_TIE, TIME_REST,
    P_LEN, P_DIV, P_SWG, P_GATE,
    P_ATK, P_DEC, P_SUS, P_REL, P_FLT, P_PIT, P_SHP, P_FX,
    P_LVL, P_PAN, P_VCE, P_GLD, P_MUTE,
    G_BPM, G_SWG,
)

# 参数字典 → ID
PARAM_IDS = {
    'LVL': P_LVL, 'ATK': P_ATK, 'DEC': P_DEC, 'SUS': P_SUS, 'REL': P_REL,
    'FLT': P_FLT, 'PIT': P_PIT, 'SHP': P_SHP, 'FX': P_FX,
    'LEN': P_LEN, 'DIV': P_DIV, 'SWG': P_SWG, 'GATE': P_GATE,
    'PAN': P_PAN, 'VCE': P_VCE, 'GLD': P_GLD, 'MUTE': P_MUTE,
}

# MIDI 音名 → 音高
NOTE_MAP = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
            'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}

def name_to_midi(name):
    """'C4' → 60, 'F#3' → 54"""
    if not name:
        return None
    name = name.strip()
    if len(name) < 2:
        return None
    try:
        octave = int(name[-1])
    except ValueError:
        return None
    pitch_name = name[:-1]
    if pitch_name not in NOTE_MAP:
        return None
    return (octave + 1) * 12 + NOTE_MAP[pitch_name]

def build_track(link, idx, track_data):
    """写入一轨：引擎、预设、参数、步进。"""
    link.select_track(idx)
    time.sleep(0.15)

    engine_name = track_data.get('engine', 'ANALOG')
    engine = ENGINES.get(engine_name, 0)
    preset = track_data.get('preset', 0)
    link.preset(engine, preset)
    time.sleep(0.3)

    params = track_data.get('params', {})
    for key, value in params.items():
        if key in PARAM_IDS:
            link.track_param(idx, PARAM_IDS[key], value)
            time.sleep(0.05)

    steps = track_data.get('steps', [])
    for step in steps:
        i = step['i']
        notes = step.get('notes', [])
        midi_notes = []
        for n in notes:
            if isinstance(n, str):
                v = name_to_midi(n)
                if v is not None:
                    midi_notes.append(v)
            elif isinstance(n, int):
                midi_notes.append(n)
        time_mode = step.get('time', TIME_NOTE)
        vel = step.get('vel', 100)
        flags = step.get('flags', 0)
        chance = step.get('chance', 100)
        hit = step.get('hit', 0)
        acc = step.get('acc', 0)
        link.write_step(idx, i, midi_notes, time_mode, vel, flags, chance, hit, acc)
        time.sleep(0.12)  # 单步 RTT ≈0.12s

def main():
    if len(sys.argv) < 4:
        print('用法: python felucca_arrange.py <slot> <bpm> <repeat>')
        sys.exit(1)

    slot = int(sys.argv[1])
    bpm = int(sys.argv[2])
    repeat = int(sys.argv[3])

    with open('arrangement.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    tracks = data.get('tracks', [])
    if not tracks:
        print('arrangement.json 缺少 tracks')
        sys.exit(1)

    link = FeluccaLink().open()
    try:
        print(f'设备: {link.info()}')

        link.set_global(G_BPM, bpm)
        time.sleep(0.1)

        for idx, track_data in enumerate(tracks[:4]):
            print(f'写入轨 {idx}...')
            build_track(link, idx, track_data)

        print(f'保存到槽位 {slot}...')
        link.save_slot(slot)
        time.sleep(0.5)

        print(f'播放槽位 {slot} × {repeat}...')
        link.play_song([(slot, repeat)])
        time.sleep(1.0)

        print(f'SONG 状态: {link.query_song()}')
        print('完成。以实际听声为准。')
    finally:
        link.close()

if __name__ == '__main__':
    main()