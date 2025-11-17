def test_api_file_syntax():
    """Test that composer2_airflow_rest_api.py has valid syntax"""
    import ast
    import os
    
    api_file = os.path.join(os.path.dirname(__file__), '..', 'distcp-incremental-tech-talk', 'cloud_function_composer2', 'composer2_airflow_rest_api.py')
    
    with open(api_file, 'r') as f:
        source = f.read()
    
    # This will raise SyntaxError if invalid
    ast.parse(source)
    assert True

def test_api_functions_exist():
    """Test that required functions exist in composer2_airflow_rest_api.py"""
    import ast
    import os
    
    api_file = os.path.join(os.path.dirname(__file__), '..', 'distcp-incremental-tech-talk', 'cloud_function_composer2', 'composer2_airflow_rest_api.py')
    
    with open(api_file, 'r') as f:
        source = f.read()
    
    tree = ast.parse(source)
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    assert 'make_composer2_web_server_request' in functions
    assert 'trigger_dag' in functions

def test_requirements_file_exists():
    """Test that requirements.txt exists and is readable"""
    import os
    
    req_file = os.path.join(os.path.dirname(__file__), '..', 'distcp-incremental-tech-talk', 'cloud_function_composer2', 'requirements.txt')
    
    assert os.path.exists(req_file)
    
    with open(req_file, 'r') as f:
        content = f.read()
    
    assert 'google-auth' in content
    assert 'requests' in content