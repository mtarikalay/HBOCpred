"""Restore the original compressed input from the GitHub distribution parts."""
from pathlib import Path
import hashlib
import json


def digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def main():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "data/large_file_parts.json").read_text())
    target = root / manifest["target"]
    if target.exists():
        if target.stat().st_size != manifest["size"] or digest(target) != manifest["sha256"]:
            raise SystemExit("Existing input differs from the frozen release; nothing was overwritten.")
        print("Verified existing input:", target.name)
        return
    parts = [root / part["path"] for part in manifest["parts"]]
    for path, expected in zip(parts, manifest["parts"]):
        if path.stat().st_size != expected["size"] or digest(path) != expected["sha256"]:
            raise SystemExit("Part checksum mismatch: " + path.name)
    temporary = target.with_name(target.name + ".assembling")
    try:
        with temporary.open("wb") as output:
            for path in parts:
                with path.open("rb") as source:
                    while chunk := source.read(1024 * 1024):
                        output.write(chunk)
        if temporary.stat().st_size != manifest["size"] or digest(temporary) != manifest["sha256"]:
            raise SystemExit("Reconstructed input checksum mismatch.")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    print("Restored and verified:", target.name, manifest["sha256"])


if __name__ == "__main__":
    main()
