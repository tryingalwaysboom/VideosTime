#!/bin/bash
cd /home/claude/videostime/ternura; mkdir -p tmp_c1
for i in 0 1 2 3 4 5; do a=$((i*345)); b=$(((i+1)*345)); [ $b -gt 2070 ] && b=2070; [ -f tmp_c1/p$i.mp4 ] || python3 render_c1.py part $a $b tmp_c1/p$i.mp4; done
echo done > tmp_c1/DONE
