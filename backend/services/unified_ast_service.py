from services.ast_service import parse_python_ast
from services.treesitter_service import parse_with_treesitter
from models.ast_models import FileASTResult

def parse_file_ast(parsed_file) -> FileASTResult:
    if not parsed_file.content:
        return FileASTResult(file_path=parsed_file.path, functions=[], classes=[], imports=[])

    if parsed_file.language == "python":
        return parse_python_ast(parsed_file.content, parsed_file.path)
    else:
        return parse_with_treesitter(parsed_file.content, parsed_file.path, parsed_file.language)

def parse_repository_ast(parsed_files) -> list[FileASTResult]:
    results = []
    for pf in parsed_files:
        if pf.content:
            results.append(parse_file_ast(pf))
    return results