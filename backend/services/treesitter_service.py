from tree_sitter_language_pack import get_parser
from models.ast_models import FunctionInfo, ClassInfo, ImportInfo, FileASTResult
from config.treesitter_config import (
    TREESITTER_LANGUAGE_MAP, FUNCTION_NODE_TYPES, CLASS_NODE_TYPES, IMPORT_NODE_TYPES,
)

def _get_node_text(node, source_bytes: bytes) -> str:
    return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")

def _find_name_node(node, source_bytes: bytes) -> str | None:
    for child in node.children:
        if child.type in ("identifier", "type_identifier", "property_identifier", "field_identifier"):
            return _get_node_text(child, source_bytes)
    return None

def _extract_arguments(node, source_bytes: bytes) -> list[str]:
    for child in node.children:
        if "parameter" in child.type:
            args = []
            for param in child.children:
                if param.type in ("identifier", "required_parameter", "optional_parameter"):
                    args.append(_get_node_text(param, source_bytes).split(":")[0].strip())
            return args
    return []

def parse_with_treesitter(file_content: str, file_path: str, language: str) -> FileASTResult:
    ts_language = TREESITTER_LANGUAGE_MAP.get(language)
    if not ts_language:
        return FileASTResult(file_path=file_path, functions=[], classes=[], imports=[],
                              parse_error=f"No Tree-sitter grammar mapped for language: {language}")

    try:
        parser = get_parser(ts_language)
        source_bytes = file_content.encode("utf-8")
        tree = parser.parse(source_bytes)
    except Exception as e:
        return FileASTResult(file_path=file_path, functions=[], classes=[], imports=[],
                              parse_error=f"Tree-sitter parse failed: {e}")

    functions: list[FunctionInfo] = []
    classes: list[ClassInfo] = []
    imports: list[ImportInfo] = []

    func_types = FUNCTION_NODE_TYPES.get(language, set())
    class_types = CLASS_NODE_TYPES.get(language, set())
    import_types = IMPORT_NODE_TYPES.get(language, set())

    def walk(node, current_class: str | None = None):
        if node.type in func_types:
            name = _find_name_node(node, source_bytes) or "<anonymous>"
            functions.append(FunctionInfo(
                name=name,
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                arguments=_extract_arguments(node, source_bytes),
                decorators=[],
                docstring=None,
                is_method=current_class is not None,
                parent_class=current_class,
                is_async="async" in _get_node_text(node, source_bytes)[:20],
            ))

        new_current_class = current_class
        if node.type in class_types:
            name = _find_name_node(node, source_bytes) or "<anonymous>"
            classes.append(ClassInfo(
                name=name,
                file_path=file_path,
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                base_classes=[],
                docstring=None,
                method_names=[],
            ))
            new_current_class = name

        if node.type in import_types:
            imports.append(ImportInfo(
                file_path=file_path,
                line=node.start_point[0] + 1,
                module=_get_node_text(node, source_bytes)[:200],
                imported_names=[],
                is_relative=False,
            ))

        for child in node.children:
            walk(child, new_current_class)

    walk(tree.root_node)

    return FileASTResult(file_path=file_path, functions=functions, classes=classes, imports=imports)