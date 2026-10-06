"""
play_chain.py — 播放多个槽位组成的链。

用法:
    python play_chain.py <slot1> <rep1> [<slot2> <rep2> ...]

例:
    python play_chain.py 0 1 1 1     # 槽A×1 → 槽B×1
"""

import sys
import time
from felucca_link import FeluccaLink

def main():
    args = sys.argv[1:]
    if len(args) < 2 or len(args) % 2 != 0:
        print('用法: python play_chain.py <slot1> <rep1> [<slot2> <rep2> ...]')
        sys.exit(1)
    rows = [(int(args[i]), int(args[i+1])) for i in range(0, len(args), 2)]

    link = FeluccaLink().open()
    try:
        link.play_song(rows)
        time.sleep(1.0)
        print(link.query_song())
    finally:
        link.close()

if __name__ == '__main__':
    main()