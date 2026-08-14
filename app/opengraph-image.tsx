import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "AI Skill Lab — practical one-to-one AI education";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function Image() {
  return new ImageResponse(
    <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "space-between", background: "#0b0d10", color: "white", padding: "68px 74px", fontFamily: "Arial, sans-serif" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16, fontSize: 28, fontWeight: 800 }}>
        <div style={{ width: 46, height: 46, borderRadius: 13, background: "#b9ff3f", color: "#0b0d10", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 900 }}>A</div>
        AI Skill Lab
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        <div style={{ fontSize: 78, lineHeight: 0.96, letterSpacing: "-4px", fontWeight: 900, maxWidth: 980 }}>Practical AI skills.<br/>Built on real projects.</div>
        <div style={{ fontSize: 25, color: "#b7bdc5" }}>1:1 · adults · kids 8–13 · teens 14–18 · teams</div>
      </div>
      <div style={{ display: "flex", gap: 14 }}>
        {['RESEARCH','CREATE','AUTOMATE','VERIFY'].map((x) => <div key={x} style={{ border: "1px solid #343b44", borderRadius: 999, padding: "10px 16px", color: x === 'VERIFY' ? '#b9ff3f' : '#d6d9dd', fontSize: 15, fontWeight: 800, letterSpacing: "1px" }}>{x}</div>)}
      </div>
    </div>,
    size,
  );
}
