"""Public API helpers for embedding OpenHands automation."""

from __future__ import annotations

import asyncio
from pathlib import Path, PurePosixPath
from typing import Dict, Iterable, Set

from openhands.controller.state.state import State
from openhands.core.config.utils import load_openhands_config
from openhands.core.main import auto_continue_response, run_controller
from openhands.core.schema import AgentState
from openhands.core.setup import generate_sid
from openhands.events.action import FileEditAction, FileWriteAction, MessageAction


def call_agent(repo_dir: str, prompt: str) -> Dict[str, str]:
    """Run OpenHands headlessly on ``repo_dir`` with ``prompt`` and return generated tests.

    Args:
        repo_dir: Absolute or relative path of the repository to operate on. The
            directory must exist and is used as the workspace for the agent.
        prompt: Natural language instruction describing the tests to create.

    Returns:
        A mapping of relative test file paths to their textual content. Both new
        tests and modified tests are included when they can be detected.

    Raises:
        FileNotFoundError: If ``repo_dir`` does not exist or is not a directory.
        RuntimeError: If the agent exits without finishing successfully.
    """

    workspace = Path(repo_dir).expanduser().resolve()
    if not workspace.is_dir():
        raise FileNotFoundError(f'Workspace directory not found: {workspace}')

    pre_existing_tests = _snapshot_test_files(workspace)

    config = load_openhands_config()
    config.runtime = 'local'
    config.workspace_base = str(workspace)
    config.enable_browser = False
    config.security.confirmation_mode = False

    initial_action = MessageAction(content=prompt)
    session_id = generate_sid(config)

    state = asyncio.run(
        run_controller(
            config=config,
            initial_user_action=initial_action,
            sid=session_id,
            fake_user_response_fn=auto_continue_response,
        )
    )

    if state is None:
        raise RuntimeError('Agent execution returned no state')

    if state.agent_state != AgentState.FINISHED:
        raise RuntimeError(
            f'Agent finished in state {state.agent_state}. Check state.outputs for details.'
        )

    post_tests = _snapshot_test_files(workspace)
    new_files = post_tests - pre_existing_tests
    touched_from_history = _extract_test_paths_from_history(state)

    all_candidate_paths: Set[Path] = set()
    all_candidate_paths.update(new_files)
    all_candidate_paths.update(touched_from_history)

    return _read_files(workspace, all_candidate_paths)


def _read_files(workspace: Path, paths: Iterable[Path]) -> Dict[str, str]:
    results: Dict[str, str] = {}
    for rel_path in sorted(paths):
        normalized = _normalize_relative_path(rel_path)
        absolute = workspace / normalized
        if not absolute.is_file():
            continue
        try:
            content = absolute.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = absolute.read_text(encoding='utf-8', errors='ignore')
        results[normalized.as_posix()] = content
    return results


def _snapshot_test_files(workspace: Path) -> Set[Path]:
    files: Set[Path] = set()
    for path in workspace.rglob('*'):
        if not path.is_file():
            continue
        relative = path.relative_to(workspace)
        if _looks_like_test_file(relative):
            files.add(relative)
    return files


def _looks_like_test_file(path: Path) -> bool:
    parts = [part.lower() for part in path.parts]
    filename = parts[-1] if parts else ''

    test_dirs = {'test', 'tests', '__tests__'}
    if any(part in test_dirs for part in parts[:-1]):
        return True

    name = filename.lower()
    if name.startswith('test'):
        return True

    test_suffixes = (
        '_test.py',
        '_tests.py',
        '_spec.py',
        '_test.ts',
        '_tests.ts',
        '_spec.ts',
        '_test.tsx',
        '_spec.tsx',
        '_test.js',
        '_tests.js',
        '_spec.js',
        'test.java',
        'tests.java',
        'test.kt',
        'tests.kt',
        'test.rs',
        'tests.rs',
        'test.go',
        'tests.go',
        'test.rb',
        'tests.rb',
        'test.swift',
        'tests.swift',
        'test.cs',
        'tests.cs',
    )
    if any(name.endswith(suffix) for suffix in test_suffixes):
        return True

    common_exts = {
        '.py',
        '.ts',
        '.tsx',
        '.js',
        '.jsx',
        '.java',
        '.kt',
        '.go',
        '.rb',
        '.rs',
        '.php',
        '.c',
        '.cpp',
        '.cs',
        '.swift',
        '.m',
        '.scala',
    }
    return any(keyword in name for keyword in ('test', 'spec')) and any(
        name.endswith(ext) for ext in common_exts
    )


def _extract_test_paths_from_history(state: State) -> Set[Path]:
    paths: Set[Path] = set()
    for event in state.history:
        relative_path: Path | None = None
        if isinstance(event, FileEditAction):
            relative_path = _normalize_relative_path(event.path)
        elif isinstance(event, FileWriteAction):
            relative_path = _normalize_relative_path(event.path)

        if relative_path and _looks_like_test_file(relative_path):
            paths.add(relative_path)
    return paths


def _normalize_relative_path(path: Path | str) -> Path:
    if isinstance(path, Path):
        text = path.as_posix()
    else:
        text = str(path).replace('\\', '/')

    pure = PurePosixPath(text)
    if pure.is_absolute():
        pure = PurePosixPath(*pure.parts[1:])

    cleaned_parts = [part for part in pure.parts if part not in ('', '.')]
    return Path(*cleaned_parts)


__all__ = ['call_agent']
