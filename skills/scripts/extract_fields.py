#!/usr/bin/env python3
"""
Extract MCP tool definitions from lebai_robot.py

This script parses the lebai_robot.py file and extracts all function
definitions with their docstrings to generate tool definitions for MCP.

Usage:
    python scripts/extract_fields.py

Output:
    Prints JSON-formatted tool definitions to stdout
"""

import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Any


def extract_all_functions(file_path: str) -> List[Dict[str, Any]]:
    """Extract all function definitions from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    functions = []
    tree = ast.parse(source_code)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Skip private functions and helpers
            if node.name.startswith('_'):
                continue
            
            docstring = ast.get_docstring(node) or ""
            
            # Get parameters
            params = []
            annotations = {}
            for arg in node.args.args:
                params.append(arg.arg)
                if arg.annotation:
                    annotations[arg.arg] = ast.unparse(arg.annotation)
            
            # Get default values
            defaults = {}
            default_start = len(params) - len(node.args.defaults)
            for i, default in enumerate(node.args.defaults):
                param_name = params[default_start + i]
                if isinstance(default, ast.Constant):
                    defaults[param_name] = default.value
                elif isinstance(default, ast.Name):
                    defaults[param_name] = default.id
                elif isinstance(default, ast.Dict):
                    defaults[param_name] = {}
                elif isinstance(default, ast.List):
                    defaults[param_name] = []
                elif isinstance(default, ast.Num):
                    defaults[param_name] = default.n
            
            functions.append({
                "name": node.name,
                "params": params,
                "annotations": annotations,
                "defaults": defaults,
                "docstring": docstring
            })
    
    return functions


def generate_mcp_tools(functions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate MCP tool definitions from function list."""
    tools = []
    
    for func in functions:
        # Skip internal functions
        if func['name'].startswith('_'):
            continue
        
        # Build properties from docstring and params
        properties = {}
        required = []
        
        # Parse docstring for parameter descriptions
        docstring = func.get('docstring', '')
        param_descriptions = {}
        
        if docstring:
            args_match = re.search(r'Args:\s*(.*?)(?:Returns:|Examples:|$)', docstring, re.DOTALL)
            if args_match:
                args_section = args_match.group(1)
                param_lines = re.findall(r'(\w+):\s*([^\n]+)', args_section)
                for param_name, param_desc in param_lines:
                    param_descriptions[param_name] = param_desc.strip()
        
        # Build properties
        for param in func['params']:
            if param == 'robot_id':
                continue
            
            param_type = func['annotations'].get(param, 'string')
            if 'int' in param_type:
                param_type = 'integer'
            elif 'float' in param_type:
                param_type = 'number'
            elif 'bool' in param_type:
                param_type = 'boolean'
            elif 'Dict' in param_type or 'dict' in param_type:
                param_type = 'object'
            elif 'List' in param_type or 'list' in param_type:
                param_type = 'array'
            else:
                param_type = 'string'
            
            prop = {
                "type": param_type,
                "description": param_descriptions.get(param, f"Parameter: {param}")
            }
            
            if param in func['defaults']:
                prop["default"] = func['defaults'][param]
            else:
                required.append(param)
            
            properties[param] = prop
        
        tool_def = {
            "name": func['name'],
            "description": func['docstring'].split('\n')[0] if func['docstring'] else f"Call {func['name']} function",
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": [p for p in required if p != 'robot_id']
            }
        }
        
        tools.append(tool_def)
    
    return {"tools": tools}


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    skills_dir = script_dir.parent
    lebai_robot_path = skills_dir / 'lebai_robot.py'
    
    if not lebai_robot_path.exists():
        print(f"Error: {lebai_robot_path} not found", file=__import__('sys').stderr)
        return 1
    
    functions = extract_all_functions(str(lebai_robot_path))
    tools = generate_mcp_tools(functions)
    print(json.dumps(tools, indent=2))
    
    return 0


if __name__ == '__main__':
    exit(main())
