import ast
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[3] / "src" / "agent_service"


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_domain_has_no_framework_or_infrastructure_dependencies():
    forbidden = ("fastapi", "sqlalchemy", "boto3", "agent_service.infra", "infra.")
    for path in (SOURCE / "domain").rglob("*.py"):
        imports = imported_modules(path)
        assert not any(module.startswith(forbidden) for module in imports), (path, imports)


def test_application_use_cases_do_not_import_concrete_infrastructure():
    for path in (SOURCE / "application" / "use_cases").glob("*.py"):
        imports = imported_modules(path)
        assert not any("infra" in module.split(".") for module in imports), (path, imports)


def test_migrated_routes_do_not_import_concrete_infrastructure():
    for name in ("build.py", "optimize.py", "export.py"):
        path = SOURCE / "api" / "routes" / name
        imports = imported_modules(path)
        assert not any("infra" in module.split(".") for module in imports), (path, imports)
