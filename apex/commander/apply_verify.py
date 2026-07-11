"""Guarded apply and verify support for Commander recommendations."""

from hashlib import sha256
from pathlib import Path

from apex.commander.recommendations import preview_recommendation


def apply_recommendation(
    finding_store,
    job_id,
    recommendation_id,
    path,
    replacement,
    approval_token,
    *,
    apply_root=None,
):
    """Apply a previewed recommendation only when the approval token still matches."""
    root_status = _resolve_target(path, apply_root)
    if root_status["status"] != "ok":
        return _blocked_apply(job_id, recommendation_id, path, root_status["status"])

    target = root_status["target"]
    preview = preview_recommendation(
        finding_store,
        job_id,
        recommendation_id,
        target,
        replacement,
    )
    if preview.get("status") != "preview_ready":
        return _blocked_apply(job_id, recommendation_id, target, preview.get("status"))

    expected_token = preview["approval"]["token"]
    if approval_token != expected_token:
        return {
            "job_id": job_id,
            "recommendation_id": recommendation_id,
            "status": "invalid_approval_token",
            "mode": "guarded_apply",
            "target": str(target),
            "expected_token": expected_token,
            "before_sha256": preview["before_sha256"],
            "after_sha256": preview["after_sha256"],
            "diff": preview["diff"],
            "verification": {"status": "not_run"},
        }

    target.write_text(replacement, encoding="utf-8")
    verification = verify_recommendation_apply(
        target,
        preview["after_sha256"],
        apply_root=apply_root,
    )
    return {
        "job_id": job_id,
        "recommendation_id": recommendation_id,
        "status": "applied" if verification["status"] == "verified" else "applied_unverified",
        "mode": "guarded_apply",
        "target": str(target),
        "before_sha256": preview["before_sha256"],
        "after_sha256": preview["after_sha256"],
        "diff": preview["diff"],
        "verification": verification,
    }


def verify_recommendation_apply(path, expected_sha256, *, apply_root=None):
    """Verify that a target file has the expected content hash."""
    root_status = _resolve_target(path, apply_root)
    if root_status["status"] != "ok":
        return {
            "status": root_status["status"],
            "target": str(path),
            "expected_sha256": expected_sha256,
            "actual_sha256": "",
        }

    target = root_status["target"]
    if not target.exists():
        return {
            "status": "target_not_found",
            "target": str(target),
            "expected_sha256": expected_sha256,
            "actual_sha256": "",
        }

    actual_sha256 = _sha256_text(target.read_text(encoding="utf-8"))
    return {
        "status": "verified" if actual_sha256 == expected_sha256 else "mismatch",
        "target": str(target),
        "expected_sha256": expected_sha256,
        "actual_sha256": actual_sha256,
    }


def _resolve_target(path, apply_root):
    if apply_root is None:
        return {"status": "apply_root_not_configured", "target": Path(path)}

    root = Path(apply_root).resolve()
    target = Path(path).resolve()
    if not _is_relative_to(target, root):
        return {"status": "outside_apply_root", "target": target}
    return {"status": "ok", "target": target}


def _is_relative_to(path, root):
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _blocked_apply(job_id, recommendation_id, path, status):
    return {
        "job_id": job_id,
        "recommendation_id": recommendation_id,
        "status": status,
        "mode": "guarded_apply",
        "target": str(path),
        "diff": "",
        "verification": {"status": "not_run"},
    }


def _sha256_text(value):
    return sha256(value.encode("utf-8")).hexdigest()
