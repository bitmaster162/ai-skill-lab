#!/usr/bin/env python3
"""T1.6F2 audited future release seal. Read-only, fail-closed and profile-bound.

Historical E3.6 is intentionally NOT_APPLICABLE; the original E3.6 checker
remains authoritative for its own release. No file writes, build or network.
"""
from __future__ import annotations
import base64
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
FUTURE = "T1_6F2_ADULT_FIRST_TASKS_R1"
HISTORICAL = "E3_6_WORKSHOP_HERO_PANEL_R1"
BASE_MAIN = "63fa9d3103e951edc3cdd801a51b0954bcb5a3fa"
BASE_TREE = "3b2a2ae99e208ac748d228528268061e2d996852"
MANIFEST_SHA = "d76f2bda459c8f40120cb79d9664205ed89bf189b121881c82bc6aea1fb3121e"
PAYLOAD_SHA = "bd972c8b657e6ebf558da3630970668f935b149abc88e28e10cc53a36d9c5973"
PREVIOUS_E36_MANIFEST_SHA = "3b762726614a3a0cf292abf23501be4f68d49df857f72bed26065e6515103c81"
PREVIOUS_E35_PINS_SHA = "c7a65c3e4dfb110bbaa573f2c7f4939ee55753215e1b86f829ab84ce5ad9037d"
DATE = "2026-10-10"
PRESERVED_PINS = {'404.html': (1952, 'c47c3d76d0cdbae30470ae3d8d4c45ccbf50a588a3973dcab9776042bde9e18f'), '98ac1c70-f355-43f0-84f5-57cbf4c68e18.txt': (37, '464000dca8907fbe778ead1e70c10110c45bb844c94a040da8ed6656c1c57329'), 'about.html': (12787, '78016dc45f5a8be438e12e724024437407e390af08e7b1d1315fdc2238cdf4b4'), 'apple-touch-icon.png': (793, '9cb88cac8049098fdfec1bb9e61bc25e9e2fa3fb8e1ac56516d06e4b332399f0'), 'build.html': (19588, '70e3d63366aebbeabf21505c7823488cf558d427b71f2e5ce576025de4561db1'), 'business.html': (36825, 'c71a4b1176484a8477b9e5f5c97c3fd5e874085acd769164ed039c46f8e9d5e2'), 'certificate.html': (12844, 'f253f34371206df5a3a2a53ceaef2623e7465b5a70476beff7d0654690637174'), 'challenge.html': (14126, '56bf5dc9e12d3eb898cf1b8e6e85e3160e6178e45032a702ef1adb7641aa6b6f'), 'curriculum.html': (18266, '7e836c31030f948cc320b7ea91a8d8c9ddaaff11a936770c021598cfdf45c095'), 'en.html': (14042, 'd9c3804919254d78fd73a8ebeaa3b6ffd42a6c2b4c7ff1d291ad929f98be2e36'), 'en/about.html': (10492, 'e5e7c89ed856beaa84b56e56694b02a78eb37a1abd8934da5ab8cdcfd3950530'), 'en/build.html': (14383, '6a963b7bacfa0f9eecf57de0299afbff8ed015299f458d2754ab3166ed080c48'), 'en/business.html': (27133, '31966492f3005b4b9f5f7747b5b75e511978d6e58502cf7a450413dc8f6964fc'), 'en/certificate.html': (9880, 'e43a3c1c5ca5ceed6c8ead1ec6412a7a363a2a1aa00d9b16451fc02696b7c232'), 'en/challenge.html': (11790, 'f381308ca6b344ed3785e8168a97768f30353a4c79a668c37b6b5705bfac7f61'), 'en/curriculum.html': (14491, '7acce68cefdd9cf91f2e72727f202959d8f9db3fb5f19347ca601d91d2326105'), 'en/family.html': (9339, '52d9880e9356d19c12ecde46d351b746c1d8e9543b5f1f64c230b087d4c11886'), 'en/faq.html': (12063, '4a880b4aefdeb54d6ffd60bb7d804441c10c95111332b7bbb72e480469a47b62'), 'en/guides/ai-safety-for-kids.html': (14890, 'a386fd8c652960faf22bf606a00fa0f23afcd26882e424d9d308166a04bd1aaf'), 'en/kids.html': (12706, '06f7f7f643ba6222df484e68e34bed7611331374d3706a3b7f62876cb56fb3a2'), 'en/matcher.html': (10434, 'fb2ab78d51a941b87b8cae4d06e8074b9584fecdd8e888d4edc6375591546650'), 'en/method.html': (7417, '65e3ab868a8f2aa2ebdcde000f3b01cfbc2acfaf17186eac32137e9b935d8617'), 'en/parents.html': (11573, 'c70ee6601a9395907cc00c51e22acf71252f814e8ebd0fcce84ae58087c3dcdd'), 'en/personal.html': (14769, 'eb2de9d3b280a9b2f542092b2dba551832cbbcd2f75e1a5e3fa132d502f0c10d'), 'en/phuket.html': (9334, '10cf9ba9f1dd0b3077b767f5b73080a5c40b75f2ece6d209b77e727afd6f5946'), 'en/pricing.html': (15898, 'd240c6ac48a372f59f650aef52e5c474b224821b540d7bb65f0a6408116583cf'), 'en/privacy.html': (8777, '1273aefe18ed6e938a55bf07776784332108bc794335dcdb12c3862f41ad1141'), 'en/projects.html': (20898, 'fb7ec221a02b3885e813beb1779b52f1c71fc752b3975801575622adee31e744'), 'en/proof.html': (22603, '49d525cc0a4ebc268cb4a3d91e880815bd34a21cef5174c5298b46cae11d5353'), 'en/safety.html': (11108, '7b276e429ff29d322a673f1e22fb611c45cfa6d2a97fd76897c673f9953aa16a'), 'en/start.html': (15916, 'baae34d9842851d09460189e1161527d39681fbdeffb21512f3f7085bc0e3f28'), 'en/studio.html': (12373, '15d863d291acb92623f0cd163f0ec50af88bb302fb586447aff7a3439a2ae8e9'), 'en/teens.html': (16540, '7643c5b46c066350f5b06d2c0114692138fb1a0905eb16fcb25707f3aa8f5f98'), 'en/terms.html': (6834, 'c0e97aefd66215d012395ec27a8f174bc0c26c9ae0b477d24789cd340e045ec9'), 'family.html': (11414, '43b8dd5d53b0682eaa05a73230f835b2930cce2a221a7b22bf940ee4da5254bb'), 'faq.html': (16082, 'c88b3d384402b816ac7926eb129c68fad6a62b577e41fb660e53d303321addee'), 'favicon.ico': (3775, 'd81acfcbbdc40f45cebffe3378706282124fec993f182cab128b9346147d9b7d'), 'favicon.svg': (234, '3530c65a4a778bb4ad243457cffd36d6d3c063b33231e1838413a97f0b4ce927'), 'fonts/Onest-ru-en.woff2': (30036, '1527f4a5e3a2c65b9d789bf86a49cceefea2472bda0b1b3edc08b3adae4a9997'), 'fonts/Unbounded-ru-en.woff2': (52016, '1600f2b8c27dc942601fdd2fc3f894f0375e371287d740289bf58945ab1991b1'), 'guides/ai-safety-for-kids.html': (18878, '6624de9e37febea478fc0e3f13ede365db82dcc7e066ff7e8eb3bac30656a31e'), 'icon-192.png': (858, '9493b6adadc37e7a0a3408e0a9e6ec014e7502c15e7adec20c49cf40a4d8f09c'), 'icon-512.png': (2432, 'd06c3ab86ab5268a5648eeeeb68a013298839d519e58bb2bed4139884c81f823'), 'index.html': (18013, 'f380d4f0d889829bd507dd32efb03a690fed5d7e51bb27b2c67bfd89de07523a'), 'kids.html': (16537, 'd869c20904db3b4f3d79e0b5fb94f1208eedfed0da2a0646ae28c7d00161d1ce'), 'lab-command.js': (2974, '967f8b85b31a079e3077dd41fe0cf66305d59895cf06211f9baf4aca443d9ea3'), 'logo.png': (7465, '80b1e1966105ece5fa5e8727d5be472bff2c9efdc0ecbf8ea0af61fc7fe52a07'), 'matcher-v2.js': (15796, '8b9b4b952e46375ead3ad01b6d6a070f52feebdef5e26a09d489d46d38e5be5b'), 'matcher.html': (12470, 'c043ad77d87a79d9838cdfaac3140ddd61e6fa14e0a6909ee468d82951bf328f'), 'method.html': (8700, '55593e20a079ef361b250635731d5409ce991182dd6058e91e44007e1d54befd'), 'og-en-business.png': (8986, 'ea2e5fe1a2707b1875685bc231c95898988498701d819f0c54d247fe22b8a551'), 'og-en-faq.png': (8276, '7c34e4daa11b6bfc4699deb0c3a2a3fa14c54d9fd914be50ca4303d88125a55c'), 'og-en-home.png': (9349, '302cdb4cecbc76d5dba39338bb2c386d0db12fa25e6f69041b72c31596199eb8'), 'og-en-kids.png': (9946, 'f4248b79cbfd65d15c30a903accee50da3bb21e9c2cbb1c6da74d0aadb195918'), 'og-en-parents.png': (11208, 'de603bccb599389f9fde47434985521bcd4a406fdb2969246d184e1e26e6ab1f'), 'og-en-personal.png': (10653, '3d0047a49199ec4d5732c21f9eae07231c565e0514acf85724da65974c65f56f'), 'og-en-phuket.png': (8208, '476dad46df2d7b13bf797c382256f7f9c1b109ede651cb8e5248eed8f21399db'), 'og-en-pricing.png': (8417, 'd4a4cfeaa09be3e424a2a1c2dfb90a62962bc0a116723ee7e7b66eaf8df506e2'), 'og-en-start.png': (7935, '8526784e01f7f718a184d7e80a4d680a894ff9c64f4bc5196b6a078ee43993d2'), 'og-en-teens.png': (8263, 'd214837b837fbc909e8159643125a92aca4ed9ba3ea4a4daa9172b86a9a1304e'), 'og-ru-business.png': (9080, 'cc4d2737c32b80abae1bb5a318e83198dc3054df1b210a519337e27f547804e6'), 'og-ru-faq.png': (7826, '60362a7fa06131799ffbfdcda11030e775e8daef8bcc22799bd9adc3bc0bd6e0'), 'og-ru-home.png': (9432, '636fdf86ef13749514f8b03c2df8913e66c97bc91f3d2f8fb4006dadcf79fefa'), 'og-ru-kids.png': (9965, '280686326263971116903712f8330763c4cb1fe9fca1a1c23745ac414bcf4972'), 'og-ru-parents.png': (11040, '8ccd91bde923c719992d06df6df77615cf8746682f6c4c21555a45dbc0ff1a5c'), 'og-ru-personal.png': (9743, 'ceaa3de7f42ee1c574877be557d5655e724a1c5408979a7d5856c9b2467b3771'), 'og-ru-phuket.png': (8379, '6011b07763303074990e6fdbcb5809ef8c8d8094b5440404fa9540e649c0644b'), 'og-ru-pricing.png': (8983, 'c1a1fee223e67774bb66f62ee7b523b6b79f3081eba1f8b7addb074ab09d705d'), 'og-ru-start.png': (7828, '7a695ab6b7eaf1916c7ad049f93ab327da7b0786a5fdd34f436cad682dbf39b6'), 'og-ru-teens.png': (9291, '33b9eb38381e28d501aec3e7c027bafcc18c6e89de782f400ae145f17f3b5808'), 'og.png': (7988, '673558d19bd5203c77db540ffd80d73f6ed8b7c791085fe92949f3d84fafd664'), 'parents.html': (14579, '4f173d638dced8bccc729ef3c3953611f83ecda2a4aa739cb7feeb7a147c1d89'), 'personal.html': (18258, '83be5caa0931c331fb8261c5e3475ca3ccf74a17e686a3d69c9c91c145557bd3'), 'phuket.html': (11799, '0cc9f3644e0d97dffbbb9da70a43f1934bd4fce7470db7817e8439b46c532c53'), 'pricing.html': (19107, '34c78eedc53ce9e68621f3a1f58f58afee757dcc3e02d60cb809ac4ab550ffb4'), 'privacy.html': (11512, '8aefcd5d1aa55b1ce600d027f26749dc3f70b96243e53833f531886a5d3a212b'), 'project-filter.js': (714, '9ffbc90afc98556eb1539629ede2876362e2a00f2b84fe20df315fc09997dc28'), 'projects.html': (27431, '20faa3626b136f857886b7b240288005d8d71786edb8330dbda6fc5eda3014b6'), 'prompt-auditor.js': (3080, 'b39ca83a8200e6ffbbefe5fbb503a85bcbb0478d92ab90c52040c44daf8c82d4'), 'proof.html': (29626, 'a5b23dac38ffabe7f8e247d75cd21b6f27871eb29c39d441b7f503071890182d'), 'robert-dumanyan-mentor.webp': (10582, '1ccb8e47747706274a47302ed1a379748269de24890b5778ab721fd62ff8251b'), 'robots.txt': (67, '332cbcca130fa5d82115641450e6b05b939f5a02243a141c7795281b5286af88'), 'safety-quiz.js': (1240, 'c2ebe9fd79afcd3b7655286cd7610ecc2c0cb7f89052a3641244494778311937'), 'safety.html': (14196, 'fc5f25d641af4f7aefa0e32a035785da62f8e71393507775211775d6d52f00ad'), 'site.webmanifest': (336, 'e81aa3eab6c8b595a0c90e7f42325e4baa8e379e463dd5207693194c0648268d'), 'start-brief.js': (3934, '6a40549cb3b1272b552e0da3d4c8b0cc11fd7ba31b4c3c84bbc5a8259650e1ae'), 'start.html': (22217, '6900581a2b9d189c625a797f41e52fd1ed156134ded0b81d27b320a9b9afe3df'), 'studio.html': (15782, 'd5e49d1199188e898285d075fa1fb3ec915b9ada4a0b832160d0780135c109df'), 'teens.html': (21271, '93d7cbf210cdee8ba0c62fbe2216d37e9f63c0125edcff9267c69936929c7e58'), 'terms.html': (8824, 'd95cb20593a84e9e7d8ce406736484d05d7dfe7609e77d6dd3e531818e93bc55'), 'workshop.css': (41174, 'a666815eb37b12ab643de504fd17e0a12255d25989c63b364ea5c58693a3da06')}
MODIFIED_PINS = {'en/guides.html': (7224, '5789cc163a22b3abeb239adc4216f26b66d3ab8d4ff571b616cb36c32796c1ea'), 'guides.html': (8528, '204556755d618585651d44d52c8c0494986943364b67cfdf27b6ee9b4232c74e'), 'llms.txt': (2427, 'd10072a8332312030a015f62f60c5ae4af48b9d5fa7c0089c628f9e02dbc93c5'), 'sitemap.xml': (4608, '7f78c4eb21189b061b8a3dd3f94c49a73077c6fed6f44b6cedbfb02458297c2c'), 'vercel.json': (4408, 'ba4fefee6a7401d7959473bc126ce743eaccacddda2fdffacb9a725afc8f049e')}
NEW_PINS = {'en/guides/ai-first-tasks-for-adults.html': (20480, 'dd43b529fac595d4ac5ea2d848de54db8dd11be761bf873b109593476f2c58aa'), 'guides/ai-first-tasks-for-adults.html': (27314, 'f3cecb6ea3f46ab64ac3d3ab16db955ab8776d5edeb0c87b3b9b46bcaae2af91')}
SOURCE_PINS = {'README.md': '36eac170fb5d428e2cca290db993527c8babe51fd428cf605ac1e791aeeba822', 'app/sitemap.ts': '0b7b9b522ac5e1192e51e6fd58b6d5d0a1b7df6ed9a45d96cd056d23b8b1de71', 'lib/guides.ts': 'ce94f3692a4f5fbdcf711e45fa201e688e3a44e4626820c41d090dd31f6d5313', 'scripts/guide_route_admission.py': 'ac3181a2496ebe548b8feec25273f037818bf3646447110d698cc22d94a929fb', 'scripts/check_workshop_d4.py': 'd77a5299fef0c2d37172461a3e27be28fe4ef214ae41df541d2cedf0ff9f952e', 'scripts/check_workshop_d5.py': 'ff4fdcfa1db0562ef036e041789bcb7b6b6e73bfdbd07f6251c56616c3ab618f'}
GUIDE_MD_PINS = {'guides/aiskillab/ai-first-tasks-for-adults.ru.md': '5c5f8d8da100a8657aeefbe5d9044462095e92db341e240a37bdebae57bba61b', 'guides/aiskillab/ai-first-tasks-for-adults.en.md': 'b0bcd0a6b545d2d8d4b190e55ab9d3c76350a9a30a8e1c745fb23e04b48df671'}
CSP_SCRIPT_HASHES = frozenset(["'sha256-+5Abet46dRu7xgh7ONU3aRHwu4XCgn0av3VtVaB9vQQ='", "'sha256-1D5p3XKYCKjFN5qkykAgO5oSy7JKiMTZDf1TbxQpxPs='", "'sha256-9zfBNf6BTpltyZT7sXvGKMaeed+z6N4SOxvJXQUlwQ8='", "'sha256-CCVgyL9wfl6vyK4MT6kQBhSDJxpdgMx5jEfjQ+hnc8s='", "'sha256-DpHqfAHUgp/L5/bQcplT9Of3U5ivdu/GpOu5eOrHV64='", "'sha256-HQqaa3Z1Xw16vqjkVC4UKBF9jlvYXnOZNhOhiExBD+M='", "'sha256-HtzNzttJwWRzqCX1wpQkWpidK7i6pRs2JvGwZcxDzx8='", "'sha256-MYAcxKb2LcjgJVHpr6CfqqUj4DachPW5lzG0UkkWZPY='", "'sha256-Mwz56/kjcl+qmxr/4Orda2ZeuN4b2iPQiYEMe+/ohRw='", "'sha256-W8CfKRZBNbzGtbnZXIMHDmyTdraCtlMMu9Y9kF7Tv9M='", "'sha256-WqigdFWh373d7RTqQ9bLDsYefW10sIr8tAkK8gVrVGY='", "'sha256-XIViPnFQEwT0xRGoh64CY3dXxozrVfMjxwurBFtpWuQ='", "'sha256-Xci1Rtuqv3/4QzsVwusXarUdqkdEJW7YGXQfBN3tONs='", "'sha256-YKkkxaOG3LfDneK5G+cpSniSqlhs60fPJC1KgutD7L4='", "'sha256-crRjSblbKaYdV0QZDHQfkTjQb8dL0L6jh1kdSKFp+cc='", "'sha256-d9IyEvw6JtxeSRtr1k4fiE7GYW71vv/JZngAehe+kCw='", "'sha256-dQ3SMhIPZlmsEwzfmA+sFw4Z/NcygWCYRF41mnR02KM='", "'sha256-dUbqRmiyR98Wa/jfc9YboqlxKPstPrE6yISEHTcUF/0='", "'sha256-ep5rhVKiiKhV3aX+EseidQI4X0hKvotM3w/rMVCCxUc='", "'sha256-ffhfSLr701n8XV3TY4Oele7DimRKw16tJ66ZKfGWLrM='", "'sha256-id8y4bpHWJhsbKClaaFAeJM9wUJhLIfVsfJg6kTiYhU='", "'sha256-mBnSpbC8d2CYfRQIfDdtUxZxquYSB/tFwkhFZK4+eNc='", "'sha256-mtQlGJdMkEh8zZt/9bFfZwO6vDkwVmoUfwZ+15TLdiQ='", "'sha256-n75S1xfHaxaMAWOpaUrbrXZ46nUAYff912gFQeHQbLM='", "'sha256-oIe1IriGV/+WLushEsKfCES0nuvc0ejg+08churdFAo='", "'sha256-pJGQTPj78KWFy+PFgRl3tlb2ZrvJkjMMHvGihIjahXw='", "'sha256-qPpJ2aGgRZeJXgr2t3KZQO3/d9/tTM8C8zOaiM7pP+k='", "'sha256-t6hwSQWdNnzYxdDm12Ac1jqTYTK39Wzt+iel101eo2Y='", "'sha256-tH5uRisYS+h78paejUhUoK5fI4MbN4goF0C9wQEbn9s='", "'sha256-uNDIziGtefWJfMdtCA7flBi99mFvnYnzWle/mYUQyf4='", "'sha256-w7WuzwQZujvHloopbyL/41RRDPnFiyskWg320lN7OWA='", "'sha256-x4yZJdgOAALgD/mAyeYqcEejzVErla6rVz4hoCA8F/4='", "'sha256-xmJCMQd4ca6dXIWouYK72T7Gbd0IolZ+XnjIlwkkr+U='", "'sha256-z+i1z6sdSHm5jJT3nLZbSrjh7AER2I3y3vEsAMPp5VI='", "'sha256-z33oO0COhbw2pcbyC11S2t5h1otemwT2zIC+uUd8lbA='", "'sha256-zHvZSfQKhrDTlvMfskNertqUc+kpFTJOzd2vr6Ejj58='", "'sha256-zzhLZEvFKoxX3OVQNEqrpxmyril76vOzdeXmMnAEerE='"])
assert len(PRESERVED_PINS) == 91 and len(MODIFIED_PINS) == 5 and len(NEW_PINS) == 2
assert len(CSP_SCRIPT_HASHES) == 37 and len(SOURCE_PINS) == 6 and len(GUIDE_MD_PINS) == 2

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

class Inline(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.on = False
        self.buf: list[str] = []
        self.scripts: list[str] = []
    def handle_starttag(self, tag, attrs):
        if tag == "script" and not dict(attrs).get("src"):
            self.on = True
            self.buf = []
    def handle_data(self, text):
        if self.on:
            self.buf.append(text)
    def handle_endtag(self, tag):
        if tag == "script" and self.on:
            self.scripts.append("".join(self.buf))
            self.on = False
            self.buf = []

def validate(overrides: Mapping[str, bytes | None] | None = None) -> dict:
    """Verify exact independent release bytes. Overrides are negative-test-only."""
    provided = {} if overrides is None else dict(overrides)
    errors: list[str] = []
    checks = 0
    def need(ok: bool, reason: str) -> None:
        nonlocal checks
        checks += 1
        if not ok:
            errors.append(reason)
    def read(rel: str) -> bytes:
        if rel in provided:
            contents = provided[rel]
            if not isinstance(contents, bytes):
                raise FileNotFoundError("override missing/nonbytes: " + rel)
            return contents
        return (ROOT / rel).read_bytes()
    def read_or_error(rel: str) -> bytes:
        try:
            return read(rel)
        except (OSError, TypeError, ValueError) as err:
            need(False, "unreadable " + rel + ": " + str(err))
            return b""

    raw_manifest = read_or_error("deploy/live/_release.json")
    need(sha(raw_manifest) == MANIFEST_SHA, "exact canonical manifest SHA")
    try:
        manifest = json.loads(raw_manifest)
    except (ValueError, UnicodeError, TypeError) as err:
        need(False, "invalid manifest JSON: " + str(err))
        return {"checks": checks, "errors": errors}
    need(isinstance(manifest, dict), "manifest must be object")
    if not isinstance(manifest, dict):
        return {"checks": checks, "errors": errors}
    need(list(manifest) == ["file_count", "files", "payload_sha256", "release_id", "schema"], "manifest canonical key order")
    need(raw_manifest == (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
         "manifest canonical two-space serialization")
    need(manifest.get("schema") == "ai-skill-lab.static-release.v1", "manifest schema")
    need(manifest.get("release_id") == FUTURE, "exact approved future release ID")
    need(type(manifest.get("file_count")) is int and manifest["file_count"] == 98, "98 file_count")
    need(manifest.get("payload_sha256") == PAYLOAD_SHA, "exact payload SHA manifest field")
    records = manifest.get("files")
    need(isinstance(records, list) and len(records) == 98, "98 canonical manifest records")
    if not isinstance(records, list):
        return {"checks": checks, "errors": errors}
    by_name: dict[str, tuple[int, str]] = {}
    for row in records:
        if not isinstance(row, dict):
            need(False, "manifest record is not object")
            continue
        need(list(row) == ["path", "sha256", "size"], "record canonical key order")
        name, size, digest = row.get("path"), row.get("size"), row.get("sha256")
        if not isinstance(name, str) or not name or ".." in name.split("/") or name.startswith("/") or "\\" in name:
            need(False, "invalid manifest asset path")
            continue
        need(name not in by_name, "duplicate manifest asset " + name)
        if name in by_name:
            continue
        need(type(size) is int and size >= 0, "manifest asset size " + name)
        need(isinstance(digest, str) and bool(re.fullmatch("[0-9a-f]{64}", digest)), "manifest asset sha " + name)
        if type(size) is int and isinstance(digest, str):
            by_name[name] = (size, digest)
    expected = {**PRESERVED_PINS, **MODIFIED_PINS, **NEW_PINS}
    need(len(expected) == 98, "91+5+2 inventory")
    need(set(by_name) == set(expected), "manifest exact 98 asset paths")
    need([row.get("path") for row in records if isinstance(row, dict)] == sorted(expected), "manifest sorted asset paths")
    for name,pin in expected.items():
        need(by_name.get(name) == pin, "independent asset pin " + name)

    actual = {path.relative_to(LIVE).as_posix()
              for path in LIVE.rglob("*") if path.is_file() and path.name != "_release.json"}
    for key, contents in provided.items():
        if not key.startswith("deploy/live/") or key == "deploy/live/_release.json":
            continue
        name = key[len("deploy/live/"):]
        if contents is None:
            actual.discard(name)
        else:
            actual.add(name)
    need(actual == set(expected), "physical 98 asset inventory, no missing/extra")
    actual_pins: dict[str, tuple[int, str]] = {}
    for name in expected:
        data = read_or_error("deploy/live/" + name)
        item = (len(data), sha(data))
        actual_pins[name] = item
        need(item == expected[name], "actual byte pin " + name)
        need(by_name.get(name) == item, "manifest matches disk " + name)
    digest = sha("".join(f"{name}\t{item[0]}\t{item[1]}\n"
                        for name,item in sorted(actual_pins.items())).encode("utf-8"))
    need(digest == PAYLOAD_SHA, "recomputed exact payload digest")
    need(sum(name.endswith(".html") for name in actual) == 55, "55 HTML files including 404")
    need(sum(size for size,_ in actual_pins.values()) == 1212095, "exact payload bytes")
    need(sum(size for name,(size,_) in actual_pins.items() if not name.endswith(".woff2")) == 1130043,
         "exact nonfont bytes")
    need(sum(size for size,_ in actual_pins.values()) <= 1200*1024, "total 1200 KiB budget")
    need(sum(size for name,(size,_) in actual_pins.items() if not name.endswith(".woff2")) <= 1120*1024,
         "nonfont 1120 KiB budget")

    for rel,digest in SOURCE_PINS.items():
        need(sha(read_or_error(rel)) == digest, "exact reviewed source " + rel)
    for rel,digest in GUIDE_MD_PINS.items():
        need(sha(read_or_error(rel)) == digest, "exact approved Markdown " + rel)
    need(sha(read_or_error("data/e3_5_heading_pins.json")) == PREVIOUS_E35_PINS_SHA,
         "historical E3.5 pin unchanged")
    need(sha(read_or_error("data/e3_6_hero_panel_pins.json")) == '5d24c15bf8d62a0ea56a2559eaf78b7b98692ca727254a124e4982b95a88070e',
         "historical E3.6 hero pins unchanged")

    xml = read_or_error("deploy/live/sitemap.xml")
    need(xml.count(b"<lastmod>2026-10-10</lastmod>") == 54, "54 exact sitemap dates")
    need(read_or_error("app/sitemap.ts").count(b'lastModified = "2026-10-10"') == 1,
         "source sitemap date once")
    try:
        tree = ET.fromstring(xml)
        locs = [node.text for node in tree.findall(".//{*}url/{*}loc")]
        need(len(locs) == 54 and len(set(locs)) == 54, "54 distinct sitemap URLs")
        need(all(isinstance(loc, str) and loc.startswith("https://aiskillab.work/") for loc in locs),
             "canonical sitemap origin")
        need("https://aiskillab.work/guides/ai-first-tasks-for-adults" in locs and
             "https://aiskillab.work/en/guides/ai-first-tasks-for-adults" in locs, "two exact adult guide URLs")
    except (ET.ParseError, TypeError) as err:
        need(False, "invalid sitemap XML: " + str(err))

    config_raw = read_or_error("deploy/live/vercel.json")
    try:
        config = json.loads(config_raw)
        header = next(x for x in config["headers"] if x["source"] == "/(.*)")
        csp = next(x["value"] for x in header["headers"] if x["key"] == "Content-Security-Policy")
        hashes = set(re.findall(r"'sha256-[^']+'", csp))
        need(hashes == CSP_SCRIPT_HASHES, "37 exact CSP hashes, no omissions/extras")
        need("'unsafe-inline'" not in csp and "'unsafe-eval'" not in csp, "no unsafe CSP directives")
        seen = set()
        for name in expected:
            if not name.endswith(".html"):
                continue
            parser = Inline()
            parser.feed(read_or_error("deploy/live/" + name).decode("utf-8"))
            for script in parser.scripts:
                if script.strip():
                    seen.add("'sha256-" + base64.b64encode(hashlib.sha256(script.encode("utf-8")).digest()).decode("ascii") + "'")
        need(seen == CSP_SCRIPT_HASHES, "CSP matches actual 55 HTML inline scripts")
    except (ValueError, TypeError, KeyError, StopIteration, UnicodeError) as err:
        need(False, "invalid CSP configuration or HTML: " + str(err))

    for name in NEW_PINS:
        try:
            html = read_or_error("deploy/live/" + name).decode("utf-8")
            need('"Article"' in html and '"BreadcrumbList"' in html, "new guide schemas " + name)
            need('hreflang="ru"' in html and 'hreflang="en"' in html and
                 'hreflang="x-default"' in html, "new guide hreflang " + name)
            need("data-lab-command-open" in html, "new guide LAB command " + name)
        except UnicodeError as err:
            need(False, "guide UTF-8 " + name + ": " + str(err))

    return {"checks": checks, "errors": errors, "release": FUTURE,
            "unchanged": len(PRESERVED_PINS), "modified": len(MODIFIED_PINS),
            "new": len(NEW_PINS), "routes": 54, "files": 98}

def main() -> int:
    try:
        manifest = json.loads((LIVE / "_release.json").read_text(encoding="utf-8"))
        release = manifest.get("release_id")
    except (OSError, TypeError, ValueError) as err:
        print("T16F2_SEAL_FAIL invalid manifest: " + str(err))
        return 1
    if release == HISTORICAL:
        print("T16F2_SEAL_NOT_APPLICABLE release=" + HISTORICAL)
        return 0
    if release != FUTURE:
        print("T16F2_SEAL_FAIL unknown release=" + repr(release))
        return 1
    result = validate()
    print("T16F2_SEAL_CHECK checks={checks} unchanged={unchanged} modified={modified} new={new} routes={routes} files={files}".format(**result))
    if result["errors"]:
        for error in result["errors"]:
            print("FAIL:", error)
        print("T16F2_SEAL_FAIL")
        return 1
    print("T16F2_SEAL_PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
