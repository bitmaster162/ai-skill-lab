from pathlib import Path

def source_path(root: Path, rel: str) -> Path:
    direct = root / rel
    if direct.exists():
        return direct
    grouped = (root / "app" / "(ru)" / "layout.tsx").exists() and (root / "app" / "(en)" / "layout.tsx").exists()
    if not grouped:
        return direct
    if rel.startswith("app/en/"):
        return root / ("app/(en)/en/" + rel.removeprefix("app/en/"))
    if rel.startswith("app/"):
        return root / ("app/(ru)/" + rel.removeprefix("app/"))
    return direct
