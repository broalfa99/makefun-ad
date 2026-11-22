#!/usr/bin/env bash
# Lays make.fun's press-pack brand badge over the clip from frame 0 and ends on the
# press-pack referral end card with our referral code typed in. Follows the ffmpeg
# recipe in https://make.fun/press/llms.txt, at 30 fps to match the clip.
set -euo pipefail
cd "$(dirname "$0")"
P=press
CLIP=clip.mp4 CODE=1mggxjac FONT=$P/JetBrainsMono-Bold.ttf
W=1080 H=1920 CARD=$P/makefun-card-9x16-transparent.webm LEN=2.5 REST=1.433 CX=210 CY=1232 CW=5 CH=78 MID=1271 SIZE=62 BADGE=$P/makefun-badge-9x16.png
HOLD=0
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$CLIP")
T=$(awk "BEGIN{print $D+$HOLD-$LEN}")
ffmpeg -hide_banner -loglevel error -y -i "$CLIP" -c:v libvpx-vp9 -i "$CARD" -i "$BADGE" -filter_complex "
[0:v]scale=$W:$H:force_original_aspect_ratio=increase,crop=$W:$H,setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=$HOLD[base];
[base][2:v]overlay=enable='lt(t,$T)',format=yuva420p,split[clip][soft];
[soft]gblur=sigma=28,eq=saturation=0.35,fade=t=in:st=$T:d=0.8:alpha=1[soft];
[clip][soft]overlay[bg];
[1:v]format=yuva420p,fps=30,setpts=PTS-STARTPTS+$T/TB[card];
[bg][card]overlay=eof_action=pass,
drawbox=x=$CX-2:y=$CY-2:w=$CW+4:h=$CH+4:color=white:t=fill:enable='gte(t,$T+$REST)',
drawtext=fontfile=$FONT:text=$CODE:fontsize=$SIZE:fontcolor=0x191419:x=$CX:y=$MID-(ascent-descent)/2:enable='gte(t,$T+$REST)'[v]" \
  -map '[v]' -map '0:a?' -c:v libx264 -preset medium -pix_fmt yuv420p -crf 20 -c:a copy -movflags +faststart makefun-pixel-loop-ad.mp4
echo "card in at $T s"
