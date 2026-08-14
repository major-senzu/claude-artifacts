"""生成物を claude-artifacts リポに commit & push し、公開URLを返す。"""
import subprocess

import config


def _git(*args: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(config.REPO_DIR), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed: {result.stderr[:500]}"
        )


def deploy(filename: str, message: str) -> str:
    url = f"{config.BASE_URL}/{filename}"
    if config.DRY_RUN:
        return url

    rel_path = str((config.PAGES_DIR / filename).relative_to(config.REPO_DIR))
    _git("add", rel_path)

    # 差分がない場合（同一内容での再修正等）は commit をスキップ
    diff = subprocess.run(
        ["git", "-C", str(config.REPO_DIR), "diff", "--cached", "--quiet"],
        timeout=60,
    )
    if diff.returncode != 0:
        _git("commit", "-m", message)
        _git("push")
    return url
