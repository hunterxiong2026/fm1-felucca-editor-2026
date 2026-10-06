// 这个文件不在浏览器里运行，而是在 DSH Agent 里作为工具调用。
// 作用：把音乐意图翻译成注入脚本的调用。

const SCALE = {
  minor:     [0,2,3,5,7,8,10],
  major:     [0,2,4,5,7,9,11],
  dorian:    [0,2,3,5,7,9,10],
  pentatonic:[0,3,5,7,10],
};

function makeBassLine(root = 36, scale = 'minor', bars = 4) {
  const steps = SCALE[scale];
  const events = [];
  for (let i = 0; i < bars * 8; i++) {
    if (Math.random() < 0.7) {
      const deg = steps[Math.floor(Math.random() * steps.length)];
      events.push({
        t: i * 250,
        pitch: root + deg,
        vel: i % 4 === 0 ? 110 : 80,
        dur: 200,
      });
    }
  }
  return events;
}

function makeChordProgression(roots = [36, 41, 43, 36], quality = 'minor') {
  const third  = quality === 'minor' ? 3 : 4;
  return roots.flatMap((r, i) => [
    { t: i * 2000,      pitch: r,         vel: 90, dur: 1800 },
    { t: i * 2000 + 10, pitch: r + third, vel: 85, dur: 1800 },
    { t: i * 2000 + 20, pitch: r + 7,     vel: 85, dur: 1800 },
  ]);
}

module.exports = { makeBassLine, makeChordProgression, SCALE };