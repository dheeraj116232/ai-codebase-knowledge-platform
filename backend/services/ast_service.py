import ast
from models.ast_models import FunctionInfo, ClassInfo, ImportInfo, FileASTResult

class PythonASTVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.functions: list[FunctionInfo] = []
        self.classes: list[ClassInfo] = []
        self.imports: list[ImportInfo] = []
        self.raw_calls: list[dict] = []
        self._current_class: str | None = None
        self._current_function: str | None = None

    def _get_decorators(self, node) -> list[str]:
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(dec.attr)
            elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                decorators.append(dec.func.id)
        return decorators

    def _get_arguments(self, node) -> list[str]:
        args = [a.arg for a in node.args.args]
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")
        return args

    def _visit_function(self, node, is_async: bool):
        func_info = FunctionInfo(
            name=node.name,
            file_path=self.file_path,
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            arguments=self._get_arguments(node),
            decorators=self._get_decorators(node),
            docstring=ast.get_docstring(node),
            is_method=self._current_class is not None,
            parent_class=self._current_class,
            is_async=is_async,
        )
        self.functions.append(func_info)

        previous_function = self._current_function
        self._current_function = node.name
        self.generic_visit(node)
        self._current_function = previous_function

    def visit_FunctionDef(self, node):
        self._visit_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node):
        self._visit_function(node, is_async=True)

    def visit_ClassDef(self, node):
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(base.attr)

        previous_class = self._current_class
        self._current_class = node.name

        method_names_before = len(self.functions)
        self.generic_visit(node)
        method_names = [f.name for f in self.functions[method_names_before:]]

        self._current_class = previous_class

        self.classes.append(ClassInfo(
            name=node.name,
            file_path=self.file_path,
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            base_classes=base_classes,
            docstring=ast.get_docstring(node),
            method_names=method_names,
        ))

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(ImportInfo(
                file_path=self.file_path,
                line=node.lineno,
                module=alias.name,
                imported_names=[alias.asname or alias.name],
                is_relative=False,
            ))

    def visit_ImportFrom(self, node):
        module = node.module or ""
        self.imports.append(ImportInfo(
            file_path=self.file_path,
            line=node.lineno,
            module=module,
            imported_names=[alias.name for alias in node.names],
            is_relative=node.level > 0,
        ))

    def visit_Call(self, node):
        if self._current_function:
            callee_name = None
            if isinstance(node.func, ast.Name):
                callee_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                callee_name = node.func.attr

            if callee_name:
                self.raw_calls.append({
                    "caller": self._current_function,
                    "callee": callee_name,
                    "line": node.lineno,
                })
        self.generic_visit(node)


def parse_python_ast(file_content: str, file_path: str) -> FileASTResult:
    try:
        tree = ast.parse(file_content, filename=file_path)
    except SyntaxError as e:
        return FileASTResult(
            file_path=file_path,
            functions=[],
            classes=[],
            imports=[],
            parse_error=f"SyntaxError: {e.msg} at line {e.lineno}",
        )

    visitor = PythonASTVisitor(file_path)
    visitor.visit(tree)

    return FileASTResult(
        file_path=file_path,
        functions=visitor.functions,
        classes=visitor.classes,
        imports=visitor.imports,
        raw_calls=visitor.raw_calls,
    )


def parse_repository_ast(parsed_files) -> list[FileASTResult]:
    results = []
    for pf in parsed_files:
        if pf.language != "python":
            continue
        if not pf.content:
            continue
        result = parse_python_ast(pf.content, pf.path)
        results.append(result)
    return results

