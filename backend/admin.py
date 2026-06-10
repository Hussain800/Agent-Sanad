"""Admin API for live policy configuration.

Allows viewing and hot-reloading the policy configuration without
restarting the server. This is a demonstration of production readiness:
MOEI can adjust thresholds and see the impact immediately.
"""
from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any

import yaml

from backend.policy.rules import load_policy
from backend.schemas import PolicyConfig


def get_policy_config() -> dict:
    """Return the current live policy configuration."""
    policy = load_policy()
    return policy.model_dump(mode="json")


def update_policy_config(updates: dict[str, Any]) -> dict:
    """Apply configuration updates and return the new state.

    Writes changes to config.yaml and reinitializes the policy cache.
    Only known PolicyConfig fields are accepted; unknown keys are rejected.
    """
    config_path = Path(__file__).resolve().parent / "policy" / "config.yaml"

    valid_fields = set(PolicyConfig.model_fields.keys())
    unknown = [k for k in updates if k not in valid_fields]
    if unknown:
        return {"error": f"unknown configuration field(s): {unknown}", "applied": False}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw = f.read()
            config = yaml.safe_load(raw) or {}
    except Exception:
        raw = ""
        config = {}

    config.update(updates)

    try:
        # Preserve comments by doing line-level updates on the raw text
        if raw:
            lines = raw.split("\n")
            new_lines = []
            updated_keys = set()
            for line in lines:
                stripped = line.strip()
                # Skip comment lines
                if stripped.startswith("#"):
                    new_lines.append(line)
                    continue
                # Check if this line starts with a key we're updating
                for key, val in updates.items():
                    if stripped.startswith(key + ":") or stripped.startswith(key + ":"):
                        # Preserve inline comment if present
                        if "#" in line:
                            comment = "  # " + line.split("#", 1)[1].strip()
                        else:
                            comment = ""
                        # Format the value properly
                        if isinstance(val, bool):
                            val_str = str(val).lower()
                        elif isinstance(val, float):
                            val_str = f"{val:.1f}" if val == int(val) else str(val)
                        else:
                            val_str = str(val)
                        indent = line[:len(line) - len(line.lstrip())]
                        new_lines.append(f"{indent}{key}: {val_str}{comment}")
                        updated_keys.add(key)
                        break
                else:
                    new_lines.append(line)
            # Add any keys not found in the file
            for key, val in updates.items():
                if key not in updated_keys:
                    if isinstance(val, bool):
                        val_str = str(val).lower()
                    elif isinstance(val, float):
                        val_str = f"{val:.1f}" if val == int(val) else str(val)
                    else:
                        val_str = str(val)
                    new_lines.append(f"{key}: {val_str}")
            with open(config_path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines) + "\n")
        else:
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    except Exception:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # Reload policy from the updated file
    reloaded = load_policy()
    return {
        "applied": True,
        "previous": {k: config.get(k) for k in updates},
        "current": reloaded.model_dump(mode="json"),
        "note": "Configuration updated. All subsequent decisions use the new thresholds.",
    }


def get_config_history() -> list[dict]:
    """Return config change history by scanning git log for config.yaml changes."""
    return []  # stub — would read from an audit table in production
