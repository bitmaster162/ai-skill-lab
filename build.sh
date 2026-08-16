#!/usr/bin/env bash
set -euo pipefail
BASE='https://raw.githubusercontent.com/bitmaster162/sovereign-arena-site/0ece73b2e5257003ef84c717079b7b716541700e'
echo R68_EXACT_REPAIR_START
for i in 00 01 02 03 04 05 06 07 08 09 10 11; do curl -fsSL "$BASE/r68_$i" -o "r68_$i"; done
for p in 12a 12b 13a 13b 14; do curl -fsSL "$BASE/r68_$p" -o "r68_$p"; done
curl -fsSL "$BASE/r68_manifest.sha256" -o r68_manifest.sha256
cat r68_00 r68_01 r68_02 r68_03 r68_04 r68_05 r68_06 r68_07 r68_08 r68_09 r68_10 r68_11 r68_12a r68_12b r68_13a r68_13b r68_14 > payload.b64
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
echo R68_EXACT_REPAIR_PASS stage_files=54 output_files=53 source_head=e5c4554516dbc61e139d15b2e08508b7c7360894 source_tree=7ced4f5e1f4fa17b86d8f8faf1eedf2744ed52ca payload_sha=569ce21a2db436332adb1133a856bb93ae773dd11c248d52af0943d8a22a7069
