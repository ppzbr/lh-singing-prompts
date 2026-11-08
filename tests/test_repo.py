"""This repository must be self-describing and internally consistent.

It is a pile of documents, so the failures worth catching are the ones documents have:

* the README and the `prompts/` folder disagreeing - a prompt nobody can find, or a
  link to a prompt that is not here;
* a `.txt` that has drifted from the `.md` beside it, so the paste-ready copy is not
  the text anyone reviewed (the README promises they are the same);
* the third-party file losing the licence text that has to travel with it;
* a MANIFEST.txt that no longer matches the tree, which is what keeps a hand-edited
  file from shipping under a stale hash.

It is deliberately small.  The path checks that the six engine repositories run are
about *their* trees; nothing here can check a path inside somebody else's project, and
this file does not pretend to.
"""

from __future__ import annotations

import hashlib
import re
from fnmatch import fnmatchcase
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "MANIFEST.txt"
PROMPTS = REPO / "prompts"

# The third-party file, and the licence text that has to ship beside it.
THIRD_PARTY = PROMPTS / "07-openutau-mcp-bridge.txt"
THIRD_PARTY_LICENCE = REPO / "LICENSE-MPL-2.0.txt"

# A prompt file name, wherever it appears - `01-synthesizer-v.md`, `all-prompts.txt`.
PROMPT_NAME_RE = re.compile(r"\b(?:all-prompts|[0-9]{2}-[a-z0-9-]+)\.(?:md|txt)\b")

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    "build",
    "bin",
    "obj",
    ".mypy_cache",
    ".ruff_cache",
}
SKIP_ENDINGS = (".egg-info", ".dist-info")
SKIP_SUFFIXES = (".pyc", ".pyo", ".lib", ".exp", ".pdb")
# Names the rest of the family's runs write.  None of them can occur here; the list is
# the union on purpose, so this file stays identical in shape across the family.
SKIP_NAMES = {
    "MANIFEST.txt",
    "LhCeVioBridge.boot.txt",
    "LhCeVioBridge.status.json",
    "LhCeVioLoader.boot.txt",
    "LhCeVioLoader.target.txt",
    "lhai_bridge.boot.txt",
    "lhai_bridge.status.json",
}
SKIP_GLOBS = (
    "*/load_host_*.exe",
    "*/hotkey_host.exe",
    "*/vocalpatch.ini",
    "*.locked-*",
)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tracked() -> set[str]:
    out = set()
    for path in REPO.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(REPO)
        if any(part in SKIP_DIRS or part.endswith(SKIP_ENDINGS) for part in rel.parts):
            continue
        if path.name.endswith(SKIP_SUFFIXES) or path.name in SKIP_NAMES:
            continue
        if any(fnmatchcase(rel.as_posix(), pattern) for pattern in SKIP_GLOBS):
            continue
        out.add(rel.as_posix())
    return out


def _manifest() -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([0-9a-f]{64})\s+(\S+)$", line)
        if match:
            entries[match.group(2)] = match.group(1)
    return entries


def _text(relative: str) -> str:
    return (REPO / relative).read_text(encoding="utf-8-sig")


# --------------------------------------------------------------------------- #
# the manifest is the record of what is here
# --------------------------------------------------------------------------- #
def test_the_manifest_lists_every_file_and_only_files_that_exist() -> None:
    listed = set(_manifest())
    present = _tracked()
    assert present - listed == set(), "in the repository but not in MANIFEST.txt"
    assert listed - present == set(), "listed in MANIFEST.txt but not in the repository"


def test_every_manifest_hash_matches_its_file() -> None:
    wrong = [name for name, want in _manifest().items() if _hash(REPO / name) != want]
    assert wrong == [], "MANIFEST.txt disagrees with the files - run tools/make-manifest.py"


def test_the_manifest_does_not_list_itself() -> None:
    assert "MANIFEST.txt" not in _manifest()


# --------------------------------------------------------------------------- #
# the README and the folder agree
# --------------------------------------------------------------------------- #
def test_every_prompt_file_is_named_in_the_readme() -> None:
    """A prompt nobody can find from the front page may as well not be here."""
    readme = _text("README.md")
    missing = sorted(
        path.name for path in PROMPTS.iterdir() if path.is_file() and path.name not in readme
    )
    assert missing == [], f"in prompts/ but never mentioned in README.md: {missing}"


def test_nothing_is_named_as_a_prompt_file_that_is_not_one() -> None:
    """The other direction, over both documents: a name that looks like a prompt file
    must resolve to one, so a rename cannot leave a dead link behind."""
    text = _text("README.md") + _text("NOTICE.md")
    named = {match.group(0) for match in PROMPT_NAME_RE.finditer(text)}
    absent = sorted(name for name in named if not (PROMPTS / name).is_file())
    assert absent == [], f"named in the documents but not in prompts/: {absent}"


# --------------------------------------------------------------------------- #
# the paste-ready copy is the text anyone reviewed
# --------------------------------------------------------------------------- #
def test_each_txt_is_the_same_text_as_the_md_beside_it() -> None:
    """The README says the two copies are the same text.  This is that claim.  The .txt
    differs on purpose in bytes only - CRLF and a UTF-8 BOM, so Notepad shows it right -
    which is why the comparison is on decoded, newline-normalised text."""
    pairs = sorted(PROMPTS.glob("*.md"))
    assert pairs, "no .md prompts at all - has the folder moved?"
    for md in pairs:
        txt = md.with_suffix(".txt")
        assert txt.is_file(), f"{md.name} has no paste-ready .txt beside it"
        a = md.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        b = txt.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        assert a == b, f"{txt.name} is not the same text as {md.name}"


def test_the_six_prompts_are_here_and_all_prompts_holds_them() -> None:
    combined = (PROMPTS / "all-prompts.txt").read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    assert combined.count("FILE: ") == 7, "all-prompts.txt should hold seven prompts"
    for path in sorted(PROMPTS.iterdir()):
        if not path.is_file() or path.name == "all-prompts.txt":
            continue
        body = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip()
        assert body in combined, f"{path.name} is missing from all-prompts.txt"


# --------------------------------------------------------------------------- #
# the third-party file travels with its licence
# --------------------------------------------------------------------------- #
def test_the_third_party_prompt_and_its_licence_text_are_both_here() -> None:
    """MPL-2.0 covers that file.  Recipients have to be told, so the file and the licence
    text are either both here or neither is - dropping one and keeping the other is the
    mistake this exists to prevent."""
    assert THIRD_PARTY.is_file(), "the third-party prompt is gone but NOTICE.md still speaks of it"
    assert THIRD_PARTY_LICENCE.is_file(), "the MPL-2.0 text has to travel with that file"
    licence = THIRD_PARTY_LICENCE.read_text(encoding="utf-8-sig")
    assert "Mozilla Public License Version 2.0" in licence
    notice = _text("NOTICE.md")
    assert THIRD_PARTY.name in notice, "NOTICE.md must name the file it is about"
    assert "MPL-2.0" in notice or "Mozilla Public License" in notice


def test_the_six_repositories_are_all_named_somewhere() -> None:
    readme = _text("README.md")
    for name in (
        "lh-synthv-mcp",
        "lh-cevio-mcp",
        "lh-voisona-mcp",
        "lh-vocaloid6-mcp",
        "lh-piapro",
        "lh-xstudio",
    ):
        assert name in readme, f"README.md no longer points at {name}"


def test_the_prompts_do_not_carry_a_placeholder_url() -> None:
    """Every prompt this repository ships as its own must install itself from a real
    repository, not from a URL the reader has to fill in."""
    offenders = []
    for path in sorted(PROMPTS.iterdir()):
        if not path.is_file() or path.name == "all-prompts.txt":
            continue
        text = path.read_text(encoding="utf-8-sig")
        for phrase in ("<the repository URL>", "<the repository folder>", "TODO", "REPLACE_ME"):
            if phrase in text:
                offenders.append(f"{path.name}: {phrase}")
    assert offenders == [], f"a prompt still carries a placeholder: {offenders}"


@pytest.mark.parametrize("name", ["README.md", "NOTICE.md"])
def test_the_documents_are_not_empty(name: str) -> None:
    assert len(_text(name)) > 500, f"{name} looks truncated"
