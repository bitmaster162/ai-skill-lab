#!/usr/bin/env bash
set -euo pipefail
echo R68_EXACT_REPAIR_START
BASE='https://raw.githubusercontent.com/bitmaster162/sovereign-arena-site/8c4110e5ad9c3df74137ed407a0d90fc966d0363/r68_exact'
for f in r68_00 r68_01 r68_02 r68_03 r68_04_07 r68_08_11 r68_12_14 r68_manifest.sha256; do curl -fsSL "$BASE/$f" -o "$f"; done
cat r68_00 r68_01 r68_02 r68_03 r68_04_07 r68_08_11 r68_12_14 > payload.b64
base64 -d payload.b64 > r68.tar.xz
echo 'c6c62dd106ba63012dcc3be54a73c93f551148bbf56898039f094a4313efe9b3  r68.tar.xz' | sha256sum -c -
test "$(stat -c%s r68.tar.xz)" = '76668'
rm -rf stage out; mkdir -p stage out
tar -xJf r68.tar.xz -C stage
test "$(find stage -type f | wc -l | tr -d ' ')" = '54'
(cd stage && sha256sum -c ../r68_manifest.sha256)
grep -q '"release_id": "R68"' stage/_release.json
grep -q '569ce21a2db436332adb1133a856bb93ae773dd11c248d52af0943d8a22a7069' stage/_release.json
find stage -mindepth 1 -maxdepth 1 ! -name vercel.json -exec cp -a {} out/ \;
test "$(find out -type f | wc -l | tr -d ' ')" = '53'
echo R68_EXACT_REPAIR_PASS stage_files=54 output_files=53 payload_sha=569ce21a2db436332adb1133a856bb93ae773dd11c248d52af0943d8a22a7069
