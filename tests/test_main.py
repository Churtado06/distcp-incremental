def test_basic_syntax():
    """Test that Python files have valid syntax"""
    import ast
    import os
    
    main_file = os.path.join(os.path.dirname(__file__), '..', 'distcp-incremental-tech-talk', 'cloud_function_composer2', 'main.py')
    
    with open(main_file, 'r') as f:
        source = f.read()
    
    # This will raise SyntaxError if invalid
    ast.parse(source)
    assert True

def test_function_exists():
    """Test that required function exists in main.py"""
    import ast
    import os
    
    main_file = os.path.join(os.path.dirname(__file__), '..', 'distcp-incremental-tech-talk', 'cloud_function_composer2', 'main.py')
    
    with open(main_file, 'r') as f:
        source = f.read()
    
    tree = ast.parse(source)
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    assert 'trigger_dag_gcf' in functions