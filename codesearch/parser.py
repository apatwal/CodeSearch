from .models import CodeSymbol
import os
import ast

SKIP_DIRS = {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}

def extract_symbols(repo_path: str) -> list[CodeSymbol]:
    symbols = []
    for dirpath, dirnames, filenames in os.walk(repo_path):
        # skip certain dirs
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            full_file_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_file_path, repo_path)

            # read full path and parse appedning codesymbols to symbols
            try:
                with open(full_file_path, encoding="utf-8") as f:
                    source = f.read()
                    tree = ast.parse(source)
                    # print(f"=== {rel_path} ===")
                    # print(ast.dump(tree, indent=2))
                    symbols.append(_make_module_symbol(tree, source, rel_path))
                    _collect(tree.body, source, rel_path, None, symbols)
            except (UnicodeDecodeError, SyntaxError):
                continue

    return symbols


def _collect(nodes, source, rel_path, parent, symbols):
    for node in nodes:
        if isinstance(node, ast.ClassDef):
            symbols.append(_make_symbol(node, "class", source, rel_path, parent))
            qualified = f"{parent}.{node.name}" if parent else node.name
            _collect(node.body, source, rel_path, qualified, symbols)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            kind = "method" if parent else "function"
            symbols.append(_make_symbol(node, kind, source, rel_path, parent))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)) and parent is None:
            for name in _assigned_names(node):
                symbols.append(_make_assignment_symbol(node, name, source, rel_path))


def _assigned_names(node):
    """Names bound by a top-level assignment, e.g. `A = 1`, `A: int = 1`, `A, B = 1, 2`."""
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    names = []
    for target in targets:
        if isinstance(target, ast.Name):
            names.append(target.id)
        elif isinstance(target, ast.Tuple):
            names.extend(e.id for e in target.elts if isinstance(e, ast.Name))
    return names


def _make_assignment_symbol(node, name, source, rel_path):
    # UPPER_CASE names are constants by convention; anything else is a module-level variable.
    kind = "constant" if name.isupper() else "variable"
    return CodeSymbol(
        path=rel_path,
        name=name,
        kind=kind,
        start_line=node.lineno,
        end_line=node.end_lineno,
        source=ast.get_source_segment(source, node),
    )


def _make_module_symbol(tree, source, rel_path):
    # "shopfront/billing/payments.py" -> "shopfront.billing.payments"; a package's
    # __init__.py is named after the package.
    module_path = os.path.splitext(rel_path)[0].split(os.sep)
    if module_path[-1] == "__init__" and len(module_path) > 1:
        module_path = module_path[:-1]
    return CodeSymbol(
        path=rel_path,
        name=".".join(module_path),
        kind="module",
        start_line=1,
        end_line=max(len(source.splitlines()), 1),
        source=source,
        docstring=ast.get_docstring(tree),
    )


def _make_symbol(node, kind, source, rel_path, parent):
    return CodeSymbol(
        path=rel_path,
        name=node.name,
        kind=kind,
        start_line=node.lineno,
        end_line=node.end_lineno,
        source=ast.get_source_segment(source, node),
        docstring=ast.get_docstring(node),
        parent=parent,
    )


if __name__ == "__main__":
    import sys
    for s in extract_symbols(sys.argv[1]):
        print(s)

    
