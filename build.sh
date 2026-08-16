#!/usr/bin/env bash
set -euo pipefail
echo R68_SELF_CONTAINED_START
cat r68_00 r68_01 r68_02 r68_03 r68_04a r68_04b r68_04c r68_04d r68_05a r68_05b r68_05c r68_05d1 r68_05d2a r68_05d2b r68_05d2c r68_06 r68_07 r68_08 > payload.b64
base64 -d payload.b64 > r68.tar.xz.decoded
echo 'c6c62dd106ba63012dcc3be54a73c93f551148bbf56898039f094a4313efe9b3  r68.tar.xz.decoded' | sha256sum -c -
test "$(stat -c%s r68.tar.xz.decoded)" = '76668'
rm -rf out
mkdir -p out
tar -xJf r68.tar.xz.decoded -C out
test "$(find out -type f | wc -l | tr -d ' ')" = '54'
echo '8d170161fb4c269eb29906bcd1aebd4f1c7d5d7dc3d0be35f2b665ad1561f9cd  out/_release.json' | sha256sum -c -
grep -q '"release_id": "R68"' out/_release.json
grep -q '569ce21a2db436332adb1133a856bb93ae773dd11c248d52af0943d8a22a7069' out/_release.json
rm out/vercel.json
test "$(find out -type f | wc -l | tr -d ' ')" = '53'
echo R68_SELF_CONTAINED_PASS source_head=e5c4554516dbc61e139d15b2e08508b7c7360894 source_tree=7ced4f5e1f4fa17b86d8f8faf1eedf2744ed52ca output_files=53
