"""
felucca_cli.py — FM-1 / Felucca 命令行工具

用法:
    python felucca_cli.py info
    python felucca_cli.py desc <scope> <id>       # scope: 0=轨道, 1=全局
    python felucca_cli.py readstep <track> <step>
    python felucca_cli.py wtest <track> <step> <note>
    python felucca_cli.py dump <track>            # 读 0..63 步
    python felucca_cli.py restore <track>         # 清空该轨所有步
    python felucca_cli.py readparam <track> <pid>
    python felucca_cli.py setparam <track> <pid> <value>
    python felucca_cli.py play <slot> <repeat>
    python felucca_cli.py stop
    python felucca_cli.py qsong
"""

import sys
from felucca_link import FeluccaLink, TIME_REST, TIME_NOTE

def cmd_info(link):
    print(link.info())

def cmd_desc(link, scope, pid):
    print(link.desc(int(scope), int(pid)))

def cmd_readstep(link, track, step):
    print(link.read_step(int(track), int(step)))

def cmd_wtest(link, track, step, note):
    link.write_step(int(track), int(step), [int(note)], TIME_NOTE, 100)
    print(f'已写轨{track} 步{step} 音{note}')

def cmd_dump(link, track):
    t = int(track)
    for i in range(64):
        s = link.read_step(t, i)
        if s and (s['n'] > 0 or s['time'] != TIME_NOTE):
            print(f'step {i:2d}: {s}')
    print('dump 完成')

def cmd_restore(link, track):
    t = int(track)
    for i in range(64):
        link.write_step(t, i, [], TIME_REST, 0)
    print(f'轨 {t} 已清空')

def cmd_readparam(link, track, pid):
    print(link.track_param(int(track), int(pid)))

def cmd_setparam(link, track, pid, value):
    link.track_param(int(track), int(pid), int(value))
    print(f'轨{track} 参数{pid} 已设为 {value}')

def cmd_play(link, slot, repeat):
    link.play_song([(int(slot), int(repeat))])
    print(f'播放槽位 {slot} × {repeat}')

def cmd_stop(link):
    link.stop_song()
    print('已停止')

def cmd_qsong(link):
    print(link.query_song())

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    link = FeluccaLink().open()
    try:
        if cmd == 'info':
            cmd_info(link)
        elif cmd == 'desc':
            cmd_desc(link, sys.argv[2], sys.argv[3])
        elif cmd == 'readstep':
            cmd_readstep(link, sys.argv[2], sys.argv[3])
        elif cmd == 'wtest':
            cmd_wtest(link, sys.argv[2], sys.argv[3], sys.argv[4])
        elif cmd == 'dump':
            cmd_dump(link, sys.argv[2])
        elif cmd == 'restore':
            cmd_restore(link, sys.argv[2])
        elif cmd == 'readparam':
            cmd_readparam(link, sys.argv[2], sys.argv[3])
        elif cmd == 'setparam':
            cmd_setparam(link, sys.argv[2], sys.argv[3], sys.argv[4])
        elif cmd == 'play':
            cmd_play(link, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 1)
        elif cmd == 'stop':
            cmd_stop(link)
        elif cmd == 'qsong':
            cmd_qsong(link)
        else:
            print(f'未知命令: {cmd}')
            print(__doc__)
    finally:
        link.close()

if __name__ == '__main__':
    main()