# Maps your internal language labels (from Step 3's EXTENSION_LANGUAGE_MAP) to
# the language name tree-sitter-language-pack expects
TREESITTER_LANGUAGE_MAP = {
    "javascript": "javascript",
    "typescript": "typescript",
    "go": "go",
    "java": "java",
    "rust": "rust",
    "cpp": "cpp",
    "c": "c",
}

# Node types that represent "function-like" and "class-like" constructs,
# per language — this varies because grammars aren't standardized across languages
FUNCTION_NODE_TYPES = {
    "javascript": {"function_declaration", "method_definition", "arrow_function"},
    "typescript": {"function_declaration", "method_definition", "arrow_function"},
    "go": {"function_declaration", "method_declaration"},
    "java": {"method_declaration", "constructor_declaration"},
    "rust": {"function_item"},
    "cpp": {"function_definition"},
    "c": {"function_definition"},
}

CLASS_NODE_TYPES = {
    "javascript": {"class_declaration"},
    "typescript": {"class_declaration", "interface_declaration"},
    "go": {"type_declaration"},  # Go uses structs, not classes — approximate
    "java": {"class_declaration", "interface_declaration"},
    "rust": {"struct_item", "impl_item", "trait_item"},
    "cpp": {"class_specifier", "struct_specifier"},
    "c": {"struct_specifier"},
}

IMPORT_NODE_TYPES = {
    "javascript": {"import_statement"},
    "typescript": {"import_statement"},
    "go": {"import_declaration"},
    "java": {"import_declaration"},
    "rust": {"use_declaration"},
    "cpp": {"preproc_include"},
    "c": {"preproc_include"},
}