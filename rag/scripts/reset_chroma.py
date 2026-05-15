from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHROMA_DIR = REPO_ROOT / "rag" / "chroma"


def clear_chroma_dir() -> None:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    for child in CHROMA_DIR.iterdir():
        if child.name == ".gitkeep":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset the local disposable ChromaDB index.")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation.")
    args = parser.parse_args()

    if not args.yes:
        response = input(f"Delete local ChromaDB index under {CHROMA_DIR}? Type 'yes' to continue: ")
        if response.strip().lower() != "yes":
            print("Reset cancelled.")
            return 1

    clear_chroma_dir()
    print(f"Reset local ChromaDB index: {CHROMA_DIR}")
    print("Rebuild with: python rag/scripts/index_vault.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
