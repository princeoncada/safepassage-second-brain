import pytest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = REPO_ROOT / "rag" / "chroma"


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "requires_index: mark test as requiring a built ChromaDB index",
    )


@pytest.fixture(scope="session", autouse=False)
def require_index():
    if not CHROMA_DIR.exists() or not any(CHROMA_DIR.iterdir()):
        pytest.skip("ChromaDB index not built. Run: python rag/scripts/index_vault.py")


@pytest.fixture(scope="session")
def retrieve():
    """Return the retrieve_chunks function for use in tests."""
    import sys

    sys.path.insert(0, str(REPO_ROOT))
    from rag.retrieval import retrieve_chunks

    return retrieve_chunks
