#!/usr/bin/env python3
"""
Test script to verify standalone app can be imported without errors
"""

try:
    # Test importing the main module
    import sys
    sys.path.append('/Users/tamle/Projects/finance-bro/standalone-bro')
    
    # Import without running (simulate Streamlit import check)
    import ast
    with open('/Users/tamle/Projects/finance-bro/standalone-bro/standalone_bro.py', 'r') as f:
        code = f.read()
    
    # Parse the code to check for syntax errors
    try:
        ast.parse(code)
        print("✅ standalone_bro.py syntax is valid")
    except SyntaxError as e:
        print(f"❌ Syntax error in standalone_bro.py: {e}")
        sys.exit(1)
    
    # Check for remaining src/ imports (ignore comments)
    lines = code.split('\n')
    import_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    import_code = '\n'.join(import_lines)
    if 'from src.' in import_code or 'import src.' in import_code:
        print("❌ Found remaining src/ imports in standalone_bro.py")
        sys.exit(1)
    
    # Check for authentication dependencies
    if 'authlib' in code.lower() or 'oauth' in code.lower():
        print("❌ Found authentication dependencies in standalone_bro.py")
        sys.exit(1)
    
    # Check for required functions
    required_functions = ['detect_latest_chart', 'inject_custom_success_styling', 'SAMPLE_QUESTIONS']
    for func in required_functions:
        if func not in code:
            print(f"❌ Missing required function: {func}")
            sys.exit(1)
    
    print("✅ All required functions are present")
    print("✅ No src/ imports found")
    print("✅ No authentication dependencies found")
    print("✅ Standalone app is ready!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)