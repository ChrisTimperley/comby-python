"""My noxfile.py."""
from __future__ import annotations

import re
from pathlib import Path
from tempfile import NamedTemporaryFile

import nox
from nox_poetry import Session, session

__all__ = [
    "fmt",
    "fmt_check",
    "lint",
    "lint_fix",
    "type_check",
    "test",
]


nox.options.error_on_external_run = True
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = [
    "fmt_check",
    "lint",
    "type_check",
    "test",
]

FILES: list[str] = [
    "src/comby/binary.py",
    "src/comby/core.py",
    "src/comby/exceptions.py",
    "src/comby/interface.py",
    "tests",
    "noxfile.py",
]


@nox.session(venv_backend="none")
def test(project: Session) -> None:
    """
    Run project's tests.

    :param project:
    :type project: Session
    """
    _ = project.run(
        # "-m",
        "pytest",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term",
        "tests",
        # *project.posargs,
    )


@nox.session(venv_backend="none")
@nox.parametrize("file_path", FILES)
def fmt(project: Session, file_path: str) -> None:
    """
    Run the project's formatting tools.

    :param project:
    :type project: Session
    :param file_path:
    :type file_path: str
    """
    _ = project.run(
        "pyment",
        "--first-line",
        "False",
        "--output",
        "reST",
        "--ignore-private",
        "False",
        "--init2class",
        "--skip-empty",
        "--write",
        file_path,
    )

    _ = project.run(
        "ruff",
        "check",
        file_path,
        "--select",
        "I",
        "--fix",
    )
    _ = project.run(
        "black",
        file_path,
    )


@nox.session(venv_backend="none")
@nox.parametrize("file_path", FILES)
def fmt_check(project: Session, file_path: str) -> None:
    """
    Run the project's formatter checking tools.

    :param project:
    :type project: Session
    :param file_path:
    :type file_path: str
    """
    _ = project.run(
        "ruff",
        "check",
        file_path,
        "--select",
        "I",
    )
    _ = project.run(
        "black",
        "--check",
        file_path,
    )


@session(venv_backend="none")
@nox.parametrize("file_path", FILES)
def lint(project: Session, file_path: str) -> None:
    """
    Run the project's linter tools.

    :param project:
    :type project: Session
    :param file_path:
    :type file_path: str
    """
    _ = project.run(
        "ruff",
        "check",
        file_path,
    )
    _ = project.run("flake8", file_path)


@session(venv_backend="none")
@nox.parametrize("file_path", FILES)
def lint_fix(project: Session, file_path: str) -> None:
    """
    Run the project's lint fixing tools.

    :param project:
    :type project: Session
    :param file_path:
    :type file_path: str
    """
    _ = project.run(
        "ruff",
        "check",
        file_path,
        "--fix",
    )


@session(venv_backend="none")
def update_typing(project: Session) -> None:
    """
    Run the project's type checking tools.

    :param project:
    :type project: Session
    """
    files = get_file_paths(include_pattern=r"\.py$", exclude_pattern=r"^\..*$")
    for ext in files:
        _ = project.run("python-typing-update", str(ext))


@session(venv_backend="none")
@nox.parametrize("file_path", FILES)
def type_check(project: Session, file_path: str) -> None:
    """
    Run the project's type checking tools.

    :param project:
    :type project: Session
    :param file_path:
    :type file_path: str
    """
    _ = project.run("mypy", file_path)


doc_env = {"PYTHONPATH": "src"}


@session(reuse_venv=False)
def licenses(project: Session) -> None:
    """
    Run the project's license tools.

    :param project:
    :type project: Session
    """
    # Generate a unique temporary file name. Poetry cannot write to the temp file directly on
    # Windows, so only use the name and allow Poetry to re-create it.
    with NamedTemporaryFile() as t:
        requirements_file = Path(t.name)

    # Install dependencies without installing the package itself:
    #   https://github.com/cjolowicz/nox-poetry/issues/680
    _ = project.run_always(
        "poetry",
        "export",
        "--without-hashes",
        f"--output={requirements_file}",
        external=True,
    )
    project.install("pip-licenses", "-r", str(requirements_file))
    _ = project.run("pip-licenses", *project.posargs)
    requirements_file.unlink()


# Note: This reuse_venv does not yet have affect due to:
#   https://github.com/wntrblm/nox/issues/488
def get_file_paths(include_pattern: str = "", exclude_pattern: str = "") -> list[str]:
    """
    Get a list of file paths that match the given include and exclude patterns.

    :param include_pattern: (Default value = "")
    :type include_pattern: str
    :param exclude_pattern: (Default value = "")
    :type exclude_pattern: str
    """
    base_path = Path()
    file_paths = []
    include_regex = re.compile(include_pattern)
    exclude_regex = re.compile(exclude_pattern)
    for path in base_path.rglob("*"):
        path_str = str(path)
        if exclude_regex.search(path_str):
            continue
        if not include_regex.search(path_str):
            continue
        file_paths.append(path_str)
    return file_paths
