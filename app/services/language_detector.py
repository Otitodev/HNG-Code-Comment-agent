import re
from typing import Optional

# Language detection patterns
LANGUAGE_PATTERNS = {
    'python': [
        r'\bdef\s+\w+\s*\(',
        r'\bclass\s+\w+\s*\(',
        r'\bimport\s+\w+',
        r'\bfrom\s+\w+\s+import',
        r':\s*$',  # Python's colon syntax
        r'\bprint\s*\(',
        r'\bif\s+.*:\s*$',
        r'\bfor\s+\w+\s+in\s+',
        r'__\w+__',  # Python dunder methods
    ],
    'javascript': [
        r'\bfunction\s+\w+\s*\(',
        r'\bconst\s+\w+\s*=',
        r'\blet\s+\w+\s*=',
        r'\bvar\s+\w+\s*=',
        r'=>',  # Arrow functions
        r'\bconsole\.\w+\s*\(',
        r'\brequire\s*\(',
        r'\bexport\s+',
        r'\bimport\s+.*\bfrom\b',
        r'{\s*$',  # JS object/function syntax
    ],
    'typescript': [
        r':\s*(string|number|boolean|any|void)',
        r'\binterface\s+\w+',
        r'\btype\s+\w+\s*=',
        r'<.*>',  # Generic types
        r'\bas\s+\w+',
        r'\bpublic\s+',
        r'\bprivate\s+',
        r'\bprotected\s+',
    ],
    'java': [
        r'\bpublic\s+class\s+\w+',
        r'\bpublic\s+static\s+void\s+main',
        r'\bpublic\s+\w+\s+\w+\s*\(',
        r'\bprivate\s+\w+\s+\w+',
        r'\bSystem\.out\.print',
        r'\bimport\s+java\.',
        r'{\s*$',
        r';\s*$',  # Semicolon endings
    ],
    'csharp': [
        r'\bpublic\s+class\s+\w+',
        r'\busing\s+System',
        r'\bnamespace\s+\w+',
        r'\bpublic\s+static\s+void\s+Main',
        r'\bConsole\.Write',
        r'\bstring\s+\w+',
        r'\bint\s+\w+',
        r'{\s*$',
    ],
    'cpp': [
        r'#include\s*<.*>',
        r'\bint\s+main\s*\(',
        r'\bstd::\w+',
        r'\bcout\s*<<',
        r'\bcin\s*>>',
        r'\bclass\s+\w+\s*{',
        r';\s*$',
        r'->\w+',
    ],
    'c': [
        r'#include\s*<.*\.h>',
        r'\bint\s+main\s*\(',
        r'\bprintf\s*\(',
        r'\bscanf\s*\(',
        r'\bmalloc\s*\(',
        r'\bfree\s*\(',
        r';\s*$',
    ],
    'go': [
        r'\bpackage\s+\w+',
        r'\bfunc\s+\w+\s*\(',
        r'\bimport\s+\(',
        r'\bfmt\.Print',
        r':=',  # Go's short variable declaration
        r'\bvar\s+\w+\s+\w+',
        r'\bgo\s+\w+\(',
    ],
    'rust': [
        r'\bfn\s+\w+\s*\(',
        r'\blet\s+\w+\s*=',
        r'\blet\s+mut\s+\w+',
        r'\bprintln!\s*\(',
        r'\bmatch\s+\w+\s*{',
        r'\bimpl\s+\w+',
        r'\bstruct\s+\w+',
        r';\s*$',
    ],
    'php': [
        r'<\?php',
        r'\$\w+',  # PHP variables
        r'\bfunction\s+\w+\s*\(',
        r'\becho\s+',
        r'\bprint\s+',
        r'\bclass\s+\w+',
        r'->\w+',  # PHP object operator
    ],
    'ruby': [
        r'\bdef\s+\w+',
        r'\bclass\s+\w+',
        r'\bmodule\s+\w+',
        r'\bputs\s+',
        r'\bprint\s+',
        r'\bend\s*$',
        r'@\w+',  # Instance variables
        r':\w+',  # Symbols
    ],
    'swift': [
        r'\bfunc\s+\w+\s*\(',
        r'\bvar\s+\w+\s*:',
        r'\blet\s+\w+\s*=',
        r'\bclass\s+\w+\s*:',
        r'\bstruct\s+\w+',
        r'\bprint\s*\(',
        r'\bimport\s+\w+',
    ],
    'kotlin': [
        r'\bfun\s+\w+\s*\(',
        r'\bval\s+\w+\s*=',
        r'\bvar\s+\w+\s*=',
        r'\bclass\s+\w+',
        r'\bprintln\s*\(',
        r'\bimport\s+\w+',
        r':\s*\w+',  # Type annotations
    ],
    'sql': [
        r'\bSELECT\s+',
        r'\bFROM\s+\w+',
        r'\bWHERE\s+',
        r'\bINSERT\s+INTO',
        r'\bUPDATE\s+\w+',
        r'\bDELETE\s+FROM',
        r'\bCREATE\s+TABLE',
        r'\bALTER\s+TABLE',
    ],
    'html': [
        r'<html',
        r'<head>',
        r'<body>',
        r'<div',
        r'<p>',
        r'<script',
        r'<style',
        r'<!DOCTYPE',
    ],
    'css': [
        r'{\s*$',
        r':\s*[^;]+;',
        r'@media',
        r'@import',
        r'#\w+\s*{',
        r'\.\w+\s*{',
        r'px|em|rem|%',
    ]
}

def detect_language(code: str) -> Optional[str]:
    """
    Detect programming language from code snippet.
    Returns the most likely language or None if uncertain.
    """
    if not code or not code.strip():
        return None
    
    code = code.lower().strip()
    scores = {}
    
    # Score each language based on pattern matches
    for language, patterns in LANGUAGE_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, code, re.MULTILINE | re.IGNORECASE))
            score += matches
        
        if score > 0:
            scores[language] = score
    
    if not scores:
        return None
    
    # Return language with highest score
    best_language = max(scores, key=scores.get)
    
    # Require minimum confidence (at least 2 pattern matches)
    if scores[best_language] >= 2:
        return best_language
    
    return None

def get_language_specific_tip_prompt(language: str) -> str:
    """Generate language-specific prompt for daily tips"""
    language_contexts = {
        'python': "Python development, focusing on Pythonic code, libraries like pandas/numpy, or Django/Flask",
        'javascript': "JavaScript development, including ES6+, Node.js, React, or modern web development",
        'typescript': "TypeScript development, type safety, interfaces, and modern JavaScript patterns",
        'java': "Java development, Spring framework, object-oriented programming, or enterprise patterns",
        'csharp': "C# development, .NET framework, LINQ, or ASP.NET",
        'cpp': "C++ development, memory management, STL, or performance optimization",
        'c': "C programming, memory management, system programming, or embedded development",
        'go': "Go development, concurrency, microservices, or system programming",
        'rust': "Rust development, memory safety, ownership, or system programming",
        'php': "PHP development, Laravel, web development, or server-side programming",
        'ruby': "Ruby development, Rails framework, or web development",
        'swift': "Swift development, iOS development, or Apple ecosystem",
        'kotlin': "Kotlin development, Android development, or JVM programming",
        'sql': "SQL databases, query optimization, or database design",
        'html': "HTML markup, semantic web, or web accessibility",
        'css': "CSS styling, responsive design, or modern CSS features"
    }
    
    context = language_contexts.get(language, f"{language} programming")
    return f"Give one short, practical tip for {context}. Include one emoji and be specific to {language}."