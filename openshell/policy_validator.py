"""OpenShell Policy Validator — schema and semantic validation for policies."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

# Optional jsonschema support
try:
    import jsonschema  # type: ignore

    _HAS_JSONSCHEMA = True
except ImportError:
    _HAS_JSONSCHEMA = False


# ---------------------------------------------------------------------------
# JSON-schema definitions (used when jsonschema is available)
# ---------------------------------------------------------------------------

_BASE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["version", "policy_name"],
    "properties": {
        "version": {"type": "string"},
        "policy_name": {"type": "string"},
        "description": {"type": "string"},
        "enforcement_mode": {"type": "string", "enum": ["strict", "permissive"]},
        "allowed_binaries": {"type": "array", "items": {"type": "string"}},
        "network_rules": {
            "type": "object",
            "properties": {
                "allow_domains": {"type": "array", "items": {"type": "string"}},
                "deny_all_other": {"type": "boolean"},
            },
        },
        "filesystem_permissions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["path", "access"],
                "properties": {
                    "path": {"type": "string"},
                    "access": {
                        "type": "string",
                        "enum": ["read_only", "read_write", "append", "none"],
                    },
                },
            },
        },
        "api_restrictions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["method"],
                "properties": {
                    "method": {"type": "string"},
                    "allow_from": {"type": "array", "items": {"type": "string"}},
                    "log_level": {"type": "string"},
                },
            },
        },
        "resource_limits": {
            "type": "object",
            "properties": {
                "max_cpu_percent": {"type": "number", "minimum": 0, "maximum": 100},
                "max_memory_mb": {"type": "integer", "minimum": 0},
                "max_file_descriptors": {"type": "integer", "minimum": 0},
                "max_processes": {"type": "integer", "minimum": 0},
                "execution_timeout_seconds": {"type": "integer", "minimum": 0},
            },
        },
    },
}


class PolicyValidator:
    """Validates OpenShell policy documents.

    Can operate in two modes:

    * **jsonschema** – uses the ``jsonschema`` library for structural checks.
    * **manual** – pure-stdlib fallback when ``jsonschema`` is unavailable.

    Example::

        validator = PolicyValidator()
        errors = validator.get_validation_errors(policy_dict)
        if errors:
            for e in errors:
                print(e)
    """

    # Valid access modes for filesystem entries
    _VALID_ACCESS_MODES = frozenset({"read_only", "read_write", "append", "none"})
    _VALID_LOG_LEVELS = frozenset({"debug", "info", "warning", "error", "critical"})
    _DOMAIN_RE = re.compile(
        r"^(\*\.)?[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$"
    )

    def validate_yaml_schema(
        self,
        policy_dict: Dict[str, Any],
        schema_type: str = "base",
    ) -> bool:
        """Validate *policy_dict* against the named JSON schema.

        Args:
            policy_dict: Parsed YAML policy document.
            schema_type:  Currently only ``"base"`` is supported.

        Returns:
            ``True`` when valid.

        Raises:
            ValueError: With a description of the first schema violation found.
        """
        schema = _BASE_SCHEMA
        if _HAS_JSONSCHEMA:
            try:
                jsonschema.validate(instance=policy_dict, schema=schema)
            except jsonschema.ValidationError as exc:
                raise ValueError(f"Schema validation error: {exc.message}") from exc
        else:
            # Minimal stdlib-based check
            errors = self._manual_base_check(policy_dict)
            if errors:
                raise ValueError("; ".join(errors))
        return True

    def validate_network_rules(self, rules: Dict[str, Any]) -> List[str]:
        """Return a list of validation errors for *rules* (empty == valid).

        Args:
            rules: The ``network_rules`` dict from a policy document.
        """
        errors: List[str] = []
        if not isinstance(rules, dict):
            errors.append("network_rules must be a mapping")
            return errors
        domains: Any = rules.get("allow_domains", [])
        if not isinstance(domains, list):
            errors.append("network_rules.allow_domains must be a list")
        else:
            for domain in domains:
                if not isinstance(domain, str):
                    errors.append(f"Domain entry must be a string: {domain!r}")
                elif not self._DOMAIN_RE.match(domain):
                    errors.append(f"Invalid domain format: {domain!r}")
        deny_all = rules.get("deny_all_other")
        if deny_all is not None and not isinstance(deny_all, bool):
            errors.append("network_rules.deny_all_other must be a boolean")
        return errors

    def validate_filesystem_permissions(
        self, permissions: List[Dict[str, Any]]
    ) -> List[str]:
        """Return validation errors for the ``filesystem_permissions`` list."""
        errors: List[str] = []
        if not isinstance(permissions, list):
            errors.append("filesystem_permissions must be a list")
            return errors
        for i, entry in enumerate(permissions):
            if not isinstance(entry, dict):
                errors.append(f"Entry #{i} must be a mapping")
                continue
            if "path" not in entry:
                errors.append(f"Entry #{i} missing required field 'path'")
            if "access" not in entry:
                errors.append(f"Entry #{i} missing required field 'access'")
            elif entry["access"] not in self._VALID_ACCESS_MODES:
                errors.append(
                    f"Entry #{i} has invalid access mode '{entry['access']}'; "
                    f"must be one of {sorted(self._VALID_ACCESS_MODES)}"
                )
        return errors

    def validate_api_restrictions(
        self, restrictions: List[Dict[str, Any]]
    ) -> List[str]:
        """Return validation errors for the ``api_restrictions`` list."""
        errors: List[str] = []
        if not isinstance(restrictions, list):
            errors.append("api_restrictions must be a list")
            return errors
        for i, entry in enumerate(restrictions):
            if not isinstance(entry, dict):
                errors.append(f"Restriction #{i} must be a mapping")
                continue
            if "method" not in entry:
                errors.append(f"Restriction #{i} missing required field 'method'")
            log_level = entry.get("log_level")
            if log_level is not None and log_level not in self._VALID_LOG_LEVELS:
                errors.append(
                    f"Restriction #{i} has invalid log_level '{log_level}'"
                )
            allow_from = entry.get("allow_from")
            if allow_from is not None and not isinstance(allow_from, list):
                errors.append(f"Restriction #{i} allow_from must be a list")
        return errors

    def validate_resource_limits(self, limits: Dict[str, Any]) -> List[str]:
        """Return validation errors for the ``resource_limits`` dict."""
        errors: List[str] = []
        if not isinstance(limits, dict):
            errors.append("resource_limits must be a mapping")
            return errors
        numeric_fields = {
            "max_cpu_percent": (0, 100),
            "max_memory_mb": (0, None),
            "max_file_descriptors": (0, None),
            "max_processes": (0, None),
            "execution_timeout_seconds": (0, None),
        }
        for field, (minimum, maximum) in numeric_fields.items():
            value = limits.get(field)
            if value is None:
                continue
            if not isinstance(value, (int, float)):
                errors.append(f"resource_limits.{field} must be numeric")
                continue
            if value < minimum:
                errors.append(
                    f"resource_limits.{field} must be >= {minimum}, got {value}"
                )
            if maximum is not None and value > maximum:
                errors.append(
                    f"resource_limits.{field} must be <= {maximum}, got {value}"
                )
        return errors

    def get_validation_errors(self, policy_dict: Dict[str, Any]) -> List[str]:
        """Return all validation errors across the entire *policy_dict*.

        Returns an empty list when the policy is fully valid.
        """
        errors: List[str] = []

        # Base fields
        errors.extend(self._manual_base_check(policy_dict))

        # Sub-sections
        if "network_rules" in policy_dict:
            sub = self.validate_network_rules(policy_dict["network_rules"])
            errors.extend(sub)

        if "filesystem_permissions" in policy_dict:
            sub = self.validate_filesystem_permissions(
                policy_dict["filesystem_permissions"]
            )
            errors.extend(sub)

        if "api_restrictions" in policy_dict:
            sub = self.validate_api_restrictions(policy_dict["api_restrictions"])
            errors.extend(sub)

        if "resource_limits" in policy_dict:
            sub = self.validate_resource_limits(policy_dict["resource_limits"])
            errors.extend(sub)

        return errors

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _manual_base_check(self, policy_dict: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        if not isinstance(policy_dict, dict):
            errors.append("Policy must be a YAML mapping")
            return errors
        for field in ("version", "policy_name"):
            if field not in policy_dict:
                errors.append(f"Missing required field: '{field}'")
            elif not isinstance(policy_dict[field], str):
                errors.append(f"Field '{field}' must be a string")
        mode = policy_dict.get("enforcement_mode")
        if mode is not None and mode not in ("strict", "permissive"):
            errors.append(
                f"enforcement_mode must be 'strict' or 'permissive', got '{mode}'"
            )
        return errors
