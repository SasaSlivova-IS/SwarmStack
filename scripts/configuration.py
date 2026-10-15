"""Shared configuration validation. Reads no project files and executes no commands."""
import copy
import math
import re

MIN_COOLDOWN = 5 * 60 * 60

SKILLS = {"grill-with-docs", "code-review", "delivery", "adhd-output", "unslop", "swarm", "loose-ends", "swarmstack"}
AUTHORITY = {"create_threads", "create_branches", "push_issue_branches", "open_prs", "merge_integration", "promote_production", "deploy"}


def local_path(value):
    return isinstance(value, str) and bool(value) and not value.startswith(("/", "\\")) and not re.match(r"^[A-Za-z]:", value) and ".." not in value.replace("\\", "/").split("/")


def validate(config):
    if not isinstance(config, dict):
        raise ValueError("configuration must be an object")
    required = {"schema_version", "status", "name", "goal", "success", "github_repository", "primary_branch", "integration_branch", "requirements_path", "glossary_path", "test_environment", "commands", "models", "budget", "authority", "human_ux_acceptance_required", "skills"}
    if not required <= set(config) or set(config) - required - {"swarm"} or config.get("schema_version") != 1 or config.get("status") != "confirmed":
        raise ValueError("use the exact v1 configuration and confirm setup first")
    for field in ["name", "goal", "success", "github_repository", "primary_branch", "integration_branch", "test_environment"]:
        value = config[field]
        if not isinstance(value, str) or not value.strip() or any(x in value for x in ["REPLACE_", "SELECT_", "\n", "\r"]):
            raise ValueError("unresolved or invalid field: " + field)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", config["github_repository"]):
        raise ValueError("github_repository must be owner/repository")
    if not all(local_path(config[f]) for f in ["requirements_path", "glossary_path"]):
        raise ValueError("requirements/glossary must use project-relative paths")
    if not isinstance(config["commands"], dict) or set(config["commands"]) != {"test", "lint", "typecheck", "build"}:
        raise ValueError("commands must name test/lint/typecheck/build, nullable when inapplicable")
    for name, command in config["commands"].items():
        if command is not None and (not isinstance(command, str) or not command.strip() or "REPLACE_" in command):
            raise ValueError("unresolved command: " + name)
    if not config["commands"]["test"]:
        raise ValueError("an actual test/check command is required")
    if not isinstance(config["authority"], dict) or set(config["authority"]) != AUTHORITY or not all(type(v) is bool for v in config["authority"].values()):
        raise ValueError("authority grants must be explicit booleans")
    if type(config["human_ux_acceptance_required"]) is not bool:
        raise ValueError("human acceptance policy must be explicit")
    budget = config["budget"]
    if not isinstance(budget, dict) or set(budget) != {"spend_limit_usd", "paid_overage", "allowed_data"}:
        raise ValueError("invalid budget fields")
    cost = budget["spend_limit_usd"]
    if type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0 or type(budget["paid_overage"]) is not bool or not isinstance(budget["allowed_data"], str) or not budget["allowed_data"].strip():
        raise ValueError("invalid budget or data permission")
    if not isinstance(config["skills"], list) or not all(isinstance(s, str) for s in config["skills"]) or not config["skills"] or len(set(config["skills"])) != len(config["skills"]) or not set(config["skills"]) <= SKILLS:
        raise ValueError("select known unique skills")
    if not {"grill-with-docs", "code-review", "swarmstack", "delivery", "adhd-output", "unslop"} <= set(config["skills"]):
        raise ValueError("select the core skills, including swarmstack for project setup")
    if "swarm" in config or "swarm" in config["skills"]:
        validate_options(config.get("swarm", {}))
    if not isinstance(config["models"], dict) or set(config["models"]) != {"frontend", "backend", "review"}:
        raise ValueError("select frontend/backend/review models from the live host")
    for model in config["models"].values():
        if not isinstance(model, dict) or set(model) != {"provider", "model", "effort"} or any(not isinstance(v, str) or not v.strip() or "SELECT_" in v for v in model.values()):
            raise ValueError("model IDs and efforts must be resolved")


def normalise_config(config):
    config = copy.deepcopy(config)
    if not isinstance(config, dict):
        raise ValueError("configuration must be an object")
    skills = config.get("skills")
    if not isinstance(skills, list) or any(not isinstance(s, str) for s in skills):
        raise ValueError("select known unique skills")
    if len(set(skills)) != len(skills):
        raise ValueError("select known unique skills")
    aliases = {"setup-project": "swarmstack", "swarmstack-help": "swarmstack"}
    config["skills"] = list(dict.fromkeys(aliases.get(s, s) for s in skills))
    return config


def validate_options(options):
    if not isinstance(options, dict) or set(options) != {"host", "orchestrator", "direction_cooldown_seconds", "status_ttl_seconds"}:
        raise ValueError("configure the swarm host, orchestrator and cooldowns first")
    if options["host"] not in {"t3", "codex", "claude", "manual"} or not isinstance(options["orchestrator"], str) or not options["orchestrator"].strip():
        raise ValueError("verify and configure one actual orchestrator identity")
    for key, minimum, maximum in [("direction_cooldown_seconds", MIN_COOLDOWN, 31536000), ("status_ttl_seconds", 0, 3600)]:
        value = options[key]
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError("invalid " + key)
    return options


