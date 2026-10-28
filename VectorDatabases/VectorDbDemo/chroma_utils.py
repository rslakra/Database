"""Helpers for the VectorDbDemo notebooks."""

from __future__ import annotations

import logging
import os
import shutil
import sys
import types
from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.telemetry.product import ProductTelemetryClient, ProductTelemetryEvent
from dotenv import load_dotenv
from langchain_community.llms import HuggingFacePipeline
from langchain_community.vectorstores import Chroma
from overrides import override
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    GenerationConfig,
    pipeline,
)

logging.getLogger("transformers").setLevel(logging.ERROR)

_NOOP_MODULE = "chroma_noop_telemetry"
DEFAULT_PERSIST_DIR = "chroma-local-db"
DEFAULT_COLLECTION_NAME = "techcrunch_articles"


def find_project_root() -> Path:
    """Return VectorDbDemo/ even when Jupyter's cwd is a parent folder."""
    for candidate in (Path.cwd(), Path.cwd() / "VectorDbDemo"):
        if (candidate / "chroma_utils.py").exists() or (candidate / ".env").exists():
            return candidate
    return Path.cwd()


def ensure_project_on_path() -> Path:
    """Add project root to sys.path so local helpers import reliably."""
    root = find_project_root()
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return root


def load_project_env() -> bool:
    """Load .env from the project root (not only from Jupyter's cwd)."""
    env_file = find_project_root() / ".env"
    loaded = load_dotenv(env_file) if env_file.exists() else load_dotenv()

    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if hf_token:
        os.environ["HF_TOKEN"] = hf_token
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token

    return loaded


def get_hf_llm(
    model_id: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    max_new_tokens: int = 128,
):
    """Local Hugging Face LLM for the QA chain (uses HF_TOKEN from .env)."""
    load_project_env()
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        raise ValueError("Set HF_TOKEN in VectorDbDemo/.env before running the QA chain.")

    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        token=token,
        clean_up_tokenization_spaces=False,
    )
    model = AutoModelForCausalLM.from_pretrained(model_id, token=token)
    if tokenizer.pad_token is None:
        tokenizer.pad_token_id = model.config.eos_token_id

    model.generation_config = GenerationConfig(
        max_new_tokens=max_new_tokens,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )

    hf_pipe = pipeline(
        task="text-generation",
        model=model,
        tokenizer=tokenizer,
        return_full_text=False,
    )
    return HuggingFacePipeline(
        pipeline=hf_pipe,
        model_id=model_id,
        pipeline_kwargs={},
    )


def get_persist_directory(name: str = DEFAULT_PERSIST_DIR) -> Path:
    """Absolute path to the Chroma folder under VectorDbDemo/ (stable Jupyter cwd)."""
    return find_project_root() / name


def persist_directory_exists(name: str = DEFAULT_PERSIST_DIR) -> bool:
    """True when a Chroma database already exists on disk."""
    return (get_persist_directory(name) / "chroma.sqlite3").exists()


def persist_archive_exists(name: str = DEFAULT_PERSIST_DIR) -> bool:
    """True when a zip backup exists for the persist folder."""
    return (find_project_root() / f"{name}.zip").exists()


def reset_persist_directory(name: str = DEFAULT_PERSIST_DIR) -> Path:
    """Delete on-disk Chroma data so the next create uses a single fresh collection."""
    clear_chroma_cache()
    db_path = get_persist_directory(name)
    if db_path.exists():
        shutil.rmtree(db_path)
    return db_path


def open_or_create_vectordb(
    documents,
    embedding,
    *,
    persist_name: str = DEFAULT_PERSIST_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
):
    """Open an existing Chroma DB, restore from zip, or create and embed documents.

    Returns (vectordb, persist_directory, collection_name, client_settings).
    """
    persist_directory = str(get_persist_directory(persist_name))
    client_settings = make_client_settings(persist_directory)
    clear_chroma_cache()

    open_kwargs = {
        "persist_directory": persist_directory,
        "embedding_function": embedding,
        "collection_name": collection_name,
        "client_settings": client_settings,
    }

    if persist_directory_exists(persist_name):
        print(f"Using existing database at {persist_directory}")
        vectordb = Chroma(**open_kwargs)
    elif persist_archive_exists(persist_name):
        print(f"Restoring from {persist_name}.zip, then opening database")
        restore_persist_directory(persist_name)
        clear_chroma_cache()
        vectordb = Chroma(**open_kwargs)
    else:
        print("Creating database and embedding documents (first run — may take a minute)")
        vectordb = Chroma.from_documents(
            documents=documents,
            embedding=embedding,
            persist_directory=persist_directory,
            collection_name=collection_name,
            client_settings=client_settings,
        )

    return vectordb, persist_directory, collection_name, client_settings


def archive_persist_directory(persist_directory: str = DEFAULT_PERSIST_DIR) -> Path:
    """Zip the on-disk Chroma folder to `<project>/<persist_directory>.zip`."""
    root = find_project_root()
    db_path = get_persist_directory(persist_directory)
    if not db_path.exists():
        raise FileNotFoundError(
            f"{db_path} not found — create the Chroma database before archiving."
        )

    archive_path = shutil.make_archive(
        str(root / persist_directory),
        "zip",
        root_dir=root,
        base_dir=persist_directory,
    )
    return Path(archive_path)


def restore_persist_directory(
    persist_directory: str = DEFAULT_PERSIST_DIR,
    archive_name: str | None = None,
) -> Path:
    """Extract a Chroma backup zip into the project folder."""
    root = find_project_root()
    archive = root / (archive_name or f"{persist_directory}.zip")
    if not archive.exists():
        raise FileNotFoundError(f"{archive} not found.")

    clear_chroma_cache()
    db_path = get_persist_directory(persist_directory)
    if db_path.exists():
        shutil.rmtree(db_path)

    shutil.unpack_archive(str(archive), extract_dir=root)
    return db_path


def _register_noop_telemetry() -> None:
    """Register a no-op telemetry client so Chroma never calls posthog."""
    if _NOOP_MODULE in sys.modules:
        return

    mod = types.ModuleType(_NOOP_MODULE)

    class NoOpTelemetry(ProductTelemetryClient):
        @override
        def capture(self, event: ProductTelemetryEvent) -> None:
            pass

    mod.NoOpTelemetry = NoOpTelemetry
    sys.modules[_NOOP_MODULE] = mod


def clear_chroma_cache() -> None:
    """Clear Chroma's in-process singleton (safe when re-running notebook cells)."""
    chromadb.api.client.SharedSystemClient.clear_system_cache()


def make_client_settings(persist_directory: str | Path | None = None) -> Settings:
    """Build Chroma Settings with persistence and telemetry fully disabled."""
    _register_noop_telemetry()
    if persist_directory is None:
        path = get_persist_directory()
    else:
        path = Path(persist_directory)
        if not path.is_absolute():
            path = get_persist_directory(str(path))
    return Settings(
        is_persistent=True,
        persist_directory=str(path),
        anonymized_telemetry=False,
        chroma_product_telemetry_impl=f"{_NOOP_MODULE}.NoOpTelemetry",
    )
