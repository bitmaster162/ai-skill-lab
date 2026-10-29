/** Exact SITE-A1/A2 successor admission for inherited R31 offline form test. */
import { createHash } from "node:crypto";
const PATCH="SITE_A1_A2_R2_20261026_DRAFT_REVIEW";
const MANIFEST="79ecdcd892a308ef3ae93b6f551a4c01e59e9a584eee39764daba5498df11889";
const ADMISSION="fb4a04354f1a99a2d2d0cc7b5364403b2b520406660cdeb9d4ce3eaf865c7034";
const PAYLOAD="9c5bcc257f49e53172abddd1b9f366e560adbbd00f269950cc408c555536efe3";
const RELEASE="PHUKET_UNIVERSE_U3_E38_DORMANT_R7B_20261015";
const HISTORIC="a8166f8a45f17df8b7359dfb62bba467c6061f61cab1db164183216d31c42bb6";
const sha = b => createHash("sha256").update(b).digest("hex");
export function verifySiteA2FormRuntime(manifestBytes, admissionBytes) {
  if (sha(manifestBytes)!==MANIFEST || sha(admissionBytes)!==ADMISSION)
    throw new Error("SITE_A2_FORM_RUNTIME_DENY SHA");
  const m=JSON.parse(manifestBytes.toString("utf8"));
  const a=JSON.parse(admissionBytes.toString("utf8"));
  if (m.patch_id!==PATCH || m.release_id!==RELEASE || m.file_count!==108
    || m.payload_sha256!==PAYLOAD || a.patch_id!==PATCH
    || a.candidate_manifest_sha256!==MANIFEST
    || a.candidate_payload_sha256!==PAYLOAD
    || a.historical_r7b_manifest_sha256!==HISTORIC
    || a.can_merge!==false || a.can_deploy!==false)
    throw new Error("SITE_A2_FORM_RUNTIME_DENY identity");
  return true;
}
