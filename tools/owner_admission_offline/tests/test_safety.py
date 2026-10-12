"""Static boundary checks: this verifier has no API or owner-signing capability."""
import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "owner_admission"


class SafetyBoundaryTest(unittest.TestCase):
    def test_no_network_or_subprocess_imports(self):
        banned = {"socket", "requests", "httpx", "urllib", "http", "subprocess",
                  "webbrowser", "selenium", "playwright", "pyautogui"}
        for file in PACKAGE.glob("*.py"):
            tree=ast.parse(file.read_text(encoding="utf-8"))
            modules=[]
            for n in ast.walk(tree):
                if isinstance(n, ast.Import):
                    modules.extend(x.name.split(".")[0] for x in n.names)
                if isinstance(n, ast.ImportFrom) and n.module:
                    modules.append(n.module.split(".")[0])
            self.assertFalse(banned.intersection(modules),f"{file.name}: forbidden import")

    def test_no_private_owner_key_generation_or_signer(self):
        for file in PACKAGE.glob("*.py"):
            src=file.read_text(encoding="utf-8")
            self.assertNotIn("Ed25519PrivateKey",src)
            self.assertNotIn(".sign(",src)

    def test_no_external_write_or_runtime_credentials(self):
        for file in PACKAGE.glob("*.py"):
            src=file.read_text(encoding="utf-8")
            for bad in ("GITHUB_TOKEN", "VERCEL_TOKEN", "GH_TOKEN", "API_KEY=", ".env"):
                self.assertNotIn(bad,src)

    def test_no_git_remote_adapter(self):
        for file in PACKAGE.glob("*.py"):
            text=file.read_text(encoding="utf-8")
            self.assertNotIn("git push",text)
            self.assertNotIn("git clone",text)
            self.assertNotIn("create_check_run",text)


if __name__ == "__main__":
    unittest.main()
