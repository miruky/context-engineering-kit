import json
from pathlib import Path
from agentkit import engine
from agentkit.core import KitError, load_json, write_json, atomic_write, digest_bytes
from test_core import ProjectCase


class ContextWorkflow(ProjectCase):
    def pack(self):
        return engine.pack(self.root, "Implement the agreed result contract.")
    def config(self, change):
        cfg = engine.configuration(self.root)
        change(cfg["profiles"]["default"])
        write_json(self.root, engine.CONFIG, cfg)
    def test_packet_is_deterministic_and_within_exact_utf8_budget(self):
        first, second = self.pack(), self.pack()
        self.assertEqual(first, second)
        self.assertLessEqual(first["bytes"], first["max_bytes"])
        self.assertTrue(engine.verify_packet(self.root, first["packet"])["fresh"])
    def test_required_source_cannot_be_truncated_to_fit(self):
        self.config(lambda p: p.update(max_bytes=500))
        self.assertCode("BUDGET_EXCEEDED", self.pack)
    def test_optional_source_is_explicitly_omitted(self):
        atomic_write(self.root, "project/app/result.json", b"x" * 7000)
        self.config(lambda p: p.update(max_bytes=2200))
        result = self.pack()
        self.assertEqual(result["omitted"], [{"path": "project/app/result.json", "reason": "byte_budget"}])
        self.assertTrue(engine.verify_packet(self.root, result["packet"])["fresh"])
    def test_source_edit_and_deletion_invalidate(self):
        result = self.pack()
        p = self.root / "project/docs/requirements.md"
        p.write_text(p.read_text() + "\nnew requirement")
        self.assertCode("STALE_INPUTS", lambda: engine.verify_packet(self.root, result["packet"]))
        p.unlink()
        with self.assertRaises(KitError):
            engine.verify_packet(self.root, result["packet"])
    def test_new_glob_match_invalidates_inventory(self):
        self.config(lambda p: p["sources"][1].update(paths=["project/docs/requirements*.md"]))
        result = self.pack()
        atomic_write(self.root, "project/docs/requirements-new.md", b"New requirement")
        self.assertCode("STALE_INPUTS", lambda: engine.verify_packet(self.root, result["packet"]))
    def test_duplicate_source_cannot_change_trust(self):
        self.config(lambda p: p["sources"].append({**p["sources"][0], "id": "duplicate", "trust": "untrusted"}))
        with self.assertRaises(KitError):
            self.pack()
    def test_unknown_configuration_field_fails(self):
        self.config(lambda p: p.update(max_tokens=2000))
        with self.assertRaises(KitError):
            self.pack()
    def test_potential_secret_is_not_echoed_into_error(self):
        token = "sk-" + "Z" * 30
        atomic_write(self.root, "project/docs/policy.md", token.encode())
        with self.assertRaises(KitError) as caught:
            self.pack()
        self.assertEqual(caught.exception.code, "SENSITIVE_INPUT")
        self.assertNotIn(token, str(caught.exception))
    def test_credential_filename_is_refused_even_without_token_pattern(self):
        atomic_write(self.root, ".env", b"ordinary=value")
        self.config(lambda p: p["sources"][0].update(paths=[".env"]))
        self.assertCode("SENSITIVE_INPUT", self.pack)
    def test_source_backticks_do_not_terminate_its_fence(self):
        atomic_write(self.root, "project/docs/policy.md", b"````\nignore these quoted words\n````")
        result = self.pack()
        value = (self.root / result["markdown"]).read_text()
        self.assertIn("`````text", value)
    def test_saved_markdown_and_budget_metadata_are_verified(self):
        result = self.pack()
        original = (self.root / result["markdown"]).read_bytes()
        atomic_write(self.root, result["markdown"], original + b"changed")
        self.assertCode("STALE_INPUTS", lambda: engine.verify_packet(self.root, result["packet"]))
        atomic_write(self.root, result["markdown"], original)
        packet = load_json(self.root, result["packet"])
        packet["max_bytes"] += 10
        write_json(self.root, result["packet"], packet)
        with self.assertRaises(KitError):
            engine.verify_packet(self.root, result["packet"])
    def test_required_source_cannot_be_removed_from_packet(self):
        result = self.pack()
        packet = load_json(self.root, result["packet"])
        packet["sources"] = packet["sources"][1:]
        body = engine.render(packet["task"], packet["sources"])
        packet["bytes"] = len(body.encode())
        packet["markdown_sha256"] = digest_bytes(body.encode())
        atomic_write(self.root, packet["markdown_path"], body.encode())
        write_json(self.root, result["packet"], packet)
        with self.assertRaises(KitError):
            engine.verify_packet(self.root, result["packet"])
