"""
play_slot.py — 播放已保存的槽位（不重新写入编曲）。

用法:
    python play_slot.py <slot> [repeat]
"""

import sys
import time
from felucca_link import FeluccaLink

def main():
    if len(sys.argv) < 2:
        print('用法: python play_slot.py <slot> [repeat]')
        sys.exit(1)
    slot = int(sys.argv[1])
    repeat = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    link = FeluccaLink().open()
    try:
        link.play_song([(slot, repeat)])
        time.sleep(1.0)
        print(link.query_song())
    finally:
        link.close()

if __name__ == '__main__':
    main()