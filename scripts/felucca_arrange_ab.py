"""
felucca_arrange_ab.py — 双槽链一键：写 A→存 A→写 B→存 B→SONG 链→播放。

用法:
    python felucca_arrange_ab.py <jsonA> <slotA> <jsonB> <slotB> <bpm> <repA> <repB>
"""

import json
import sys
import time
from felucca_link import FeluccaLink, G_BPM
from felucca_arrange import build_track

def load_and_write(link, json_path, slot):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    tracks = data.get('tracks', [])
    for idx, track_data in enumerate(tracks[:4]):
        print(f'  写轨 {idx}...')
        build_track(link, idx, track_data)
    link.save_slot(slot)
    time.sleep(0.5)
    print(f'  已存槽位 {slot}')

def main():
    if len(sys.argv) < 8:
        print('用法: felucca_arrange_ab.py <jsonA> <slotA> <jsonB> <slotB> <bpm> <repA> <repB>')
        sys.exit(1)

    json_a, slot_a = sys.argv[1], int(sys.argv[2])
    json_b, slot_b = sys.argv[3], int(sys.argv[4])
    bpm = int(sys.argv[5])
    rep_a, rep_b = int(sys.argv[6]), int(sys.argv[7])

    link = FeluccaLink().open()
    try:
        print(f'设备: {link.info()}')
        link.set_global(G_BPM, bpm)
        time.sleep(0.1)

        print(f'=== 写入 A: {json_a} → 槽位 {slot_a} ===')
        load_and_write(link, json_a, slot_a)

        print(f'=== 写入 B: {json_b} → 槽位 {slot_b} ===')
        load_and_write(link, json_b, slot_b)

        print(f'=== SONG 链: 槽{slot_a}×{rep_a} → 槽{slot_b}×{rep_b} ===')
        link.play_song([(slot_a, rep_a), (slot_b, rep_b)])
        time.sleep(1.0)
        print(f'SONG: {link.query_song()}')
        print('完成。')
    finally:
        link.close()

if __name__ == '__main__':
    main()