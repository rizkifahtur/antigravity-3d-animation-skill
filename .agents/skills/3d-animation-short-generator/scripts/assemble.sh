#!/usr/bin/env bash
# Assemble approved shot clips into main.mp4, then (optionally) mix BGM with ducking into final.mp4.
#
# Usage:
#   assemble.sh <project_dir> <aspect> <clip1.mp4> <clip2.mp4> ... [--bgm path/to/bgm.mp3] [--bgm-vol 0.35]
#   aspect: 16:9 | 9:16 | 1:1 | 4:5   (1:1 and 4:5 are center-cropped from the rendered clips)
#
# Clips must be passed in the exact shot order of the approved table, latest approved version each.
# Requires ffmpeg.
set -euo pipefail

proj="$1"; aspect="$2"; shift 2
clips=(); bgm=""; bgmvol="0.35"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --bgm) bgm="$2"; shift 2;;
    --bgm-vol) bgmvol="$2"; shift 2;;
    *) clips+=("$1"); shift;;
  esac
done
[[ ${#clips[@]} -gt 0 ]] || { echo "no clips given" >&2; exit 1; }
command -v ffmpeg >/dev/null || { echo "ffmpeg not found" >&2; exit 1; }

case "$aspect" in
  16:9) W=1920; H=1080;;
  9:16) W=1080; H=1920;;
  1:1)  W=1080; H=1080;;
  4:5)  W=1080; H=1350;;
  *) echo "unsupported aspect $aspect" >&2; exit 1;;
esac

out="$proj/09-assembly"; mkdir -p "$out"
inputs=(); filt=""; n=${#clips[@]}
for i in "${!clips[@]}"; do
  inputs+=(-i "${clips[$i]}")
  # scale to cover, center-crop, constant fps; add silent audio if a clip has none
  filt+="[$i:v]scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},fps=24,setsar=1,format=yuv420p[v$i];"
done
# audio: use each clip's audio, or generate silence of matching length when missing
for i in "${!clips[@]}"; do
  if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "${clips[$i]}" | grep -q .; then
    filt+="[$i:a]aresample=48000,aformat=channel_layouts=stereo[a$i];"
  else
    d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "${clips[$i]}")
    filt+="anullsrc=r=48000:cl=stereo,atrim=duration=${d}[a$i];"
  fi
done
for i in "${!clips[@]}"; do filt+="[v$i][a$i]"; done
filt+="concat=n=${n}:v=1:a=1[v][a]"

ffmpeg -y -hide_banner -loglevel error "${inputs[@]}" -filter_complex "$filt" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k "$out/main.mp4"
echo "saved $out/main.mp4"

if [[ -n "$bgm" ]]; then
  # loop BGM to film length, duck it under the clip audio (dialogue/SFX), fade out at the end
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out/main.mp4")
  fade_st=$(awk -v d="$dur" 'BEGIN{s=d-2; if(s<0)s=0; print s}')
  ffmpeg -y -hide_banner -loglevel error -i "$out/main.mp4" -stream_loop -1 -i "$bgm" -filter_complex \
    "[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=${bgmvol},atrim=duration=${dur},afade=t=out:st=${fade_st}:d=2[bg];\
     [0:a]asplit=2[sc][dry];\
     [bg][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];\
     [dry][duck]amix=inputs=2:duration=first:normalize=0[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k "$out/final.mp4"
  echo "saved $out/final.mp4"
fi
