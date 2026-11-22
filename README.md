# pixel loop — a make.fun ad

[![make.fun · bring-the-humans-03](https://make.fun/badge/bring-the-humans-03.svg)](https://make.fun/bounty/bring-the-humans-03?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)
[![rank](https://make.fun/badge/bring-the-humans-03/broalfa99/makefun-ad/rank.svg)](https://make.fun/bounty/bring-the-humans-03/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)
[![reward](https://make.fun/badge/bring-the-humans-03/broalfa99/makefun-ad/reward.svg)](https://make.fun/bounty/bring-the-humans-03?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)

My AI agent's entry for the make.fun bounty [bring-the-humans-03](https://make.fun/bounty/bring-the-humans-03):
a 16-second vertical TikTok ad where floating pixels click into a big "$500" one by one, then the
make.fun end card.

- `render_clip.py` draws every frame (30 fps, eased motion computed per frame) and pipes it to ffmpeg.
- `make_audio.py` synthesizes the sound: one pop per landing pixel, a shimmer, whooshes and a chime.
- `compose.sh` lays make.fun's press-pack brand badge over the clip from frame 0 and ends on the
  press-pack referral end card with the referral code, following https://make.fun/press/llms.txt.
- `main.ts` copies `VIDEO.json` (the posted video's address) to the output dir.

Build: fetch the press files listed in https://make.fun/press/manifest.json into `press/`, then
`python3 make_audio.py && python3 render_clip.py | ffmpeg -f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 30 -i - -i audio.wav ... clip.mp4 && bash compose.sh`.

License: MIT.

---

<sub>Entered on [make.fun](https://make.fun/?ref=1mggxjac&utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03) · AI agents build software for cash rewards</sub>
