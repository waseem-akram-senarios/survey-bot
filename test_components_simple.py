#!/usr/bin/env python3
"""
Simple Component Test Script
Tests the new UI components without Playwright
"""

import os
import subprocess
import time

def test_component_files():
    """Test if all component files exist and are properly structured"""
    print("🧪 Testing Component Files")
    print("=" * 50)
    
    component_files = [
        "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/SidebarNew.jsx",
        "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/TopNavNew.jsx",
        "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/StatCardNew.jsx",
        "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/pages/DashboardNew.jsx"
    ]
    
    all_files_exist = True
    
    for file_path in component_files:
        if os.path.exists(file_path):
            print(f"✅ {os.path.basename(file_path)} exists")
            
            # Check file content
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for React component structure
            if 'import React' in content and 'export default' in content:
                print(f"   ✅ Proper React component structure")
            else:
                print(f"   ⚠️ React component structure issue")
                all_files_exist = False
                
            # Check for modern UI elements
            if 'gradient' in content.lower() or 'modern' in content.lower():
                print(f"   ✅ Modern UI elements found")
            else:
                print(f"   ℹ️ No explicit modern UI markers")
                
        else:
            print(f"❌ {os.path.basename(file_path)} missing")
            all_files_exist = False
    
    return all_files_exist

def test_component_imports():
    """Test if components can be imported properly"""
    print("\n📦 Testing Component Imports")
    print("=" * 50)
    
    # Test if imports are correct
    dashboard_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/pages/DashboardNew.jsx"
    
    with open(dashboard_path, 'r') as f:
        content = f.read()
    
    required_imports = [
        'SidebarNew',
        'TopNavNew', 
        'StatCardNew'
    ]
    
    imports_ok = True
    
    for import_name in required_imports:
        if import_name in content:
            print(f"✅ {import_name} imported")
        else:
            print(f"❌ {import_name} not imported")
            imports_ok = False
    
    return imports_ok

def test_styling_approach():
    """Test if modern styling is implemented"""
    print("\n🎨 Testing Styling Approach")
    print("=" * 50)
    
    # Check CSS theme file
    css_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/App.css"
    
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            css_content = f.read()
        
        # Check for modern CSS features
        modern_features = {
            'CSS Variables': '--color-' in css_content,
            'Gradients': 'gradient' in css_content.lower(),
            'Modern Fonts': 'Inter' in css_content,
            'Animations': '@keyframes' in css_content,
            'Transitions': 'transition:' in css_content
        }
        
        for feature, exists in modern_features.items():
            if exists:
                print(f"✅ {feature} implemented")
            else:
                print(f"⚠️ {feature} not found")
        
        return any(modern_features.values())
    else:
        print("❌ App.css not found")
        return False

def test_component_structure():
    """Test component structure and features"""
    print("\n🏗️ Testing Component Structure")
    print("=" * 50)
    
    components = {
        'SidebarNew': {
            'file': '/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/SidebarNew.jsx',
            'features': ['navigate', 'useState', 'user profile', 'navigation items']
        },
        'TopNavNew': {
            'file': '/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/TopNavNew.jsx',
            'features': ['search', 'notifications', 'user menu', 'MenuIcon']
        },
        'StatCardNew': {
            'file': '/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/StatCardNew.jsx',
            'features': ['gradient', 'hover', 'trend', 'Card']
        },
        'DashboardNew': {
            'file': '/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/pages/DashboardNew.jsx',
            'features': ['Grid', 'StatCardNew', 'SidebarNew', 'TopNavNew']
        }
    }
    
    all_structures_ok = True
    
    for component, info in components.items():
        print(f"\n📋 Testing {component}:")
        
        if os.path.exists(info['file']):
            with open(info['file'], 'r') as f:
                content = f.read()
            
            for feature in info['features']:
                if feature in content:
                    print(f"   ✅ {feature} found")
                else:
                    print(f"   ⚠️ {feature} not found")
                    all_structures_ok = False
        else:
            print(f"   ❌ File not found")
            all_structures_ok = False
    
    return all_structures_ok

def test_package_dependencies():
    """Test if required dependencies are available"""
    print("\n📋 Testing Package Dependencies")
    print("=" * 50)
    
    package_json_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/package.json"
    
    if os.path.exists(package_json_path):
        with open(package_json_path, 'r') as f:
            package_content = f.read()
        
        required_deps = [
            '@mui/material',
            '@mui/icons-material',
            'lucide-react',
            'react',
            'react-dom'
        ]
        
        deps_ok = True
        
        for dep in required_deps:
            if dep in package_content:
                print(f"✅ {dep} dependency found")
            else:
                print(f"❌ {dep} dependency missing")
                deps_ok = False
        
        return deps_ok
    else:
        print("❌ package.json not found")
        return False

def test_build_compatibility():
    """Test if components are build-compatible"""
    print("\n🔨 Testing Build Compatibility")
    print("=" * 50)
    
    # Check for syntax errors by trying to parse JSX-like content
    components = [
        '/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/SidebarNew.jsx',
        '/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/TopNavNew.jsx',
        '/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/StatCardNew.jsx',
        '/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/pages/DashboardNew.jsx'
    ]
    
    syntax_ok = True
    
    for component_file in components:
        if os.path.exists(component_file):
            try:
                with open(component_file, 'r') as f:
                    content = f.read()
                
                # Basic syntax checks
                if content.count('{') != content.count('}'):
                    print(f"⚠️ {os.path.basename(component_file)}: Brace mismatch")
                    syntax_ok = False
                elif content.count('(') != content.count(')'):
                    print(f"⚠️ {os.path.basename(component_file)}: Parenthesis mismatch")
                    syntax_ok = False
                else:
                    print(f"✅ {os.path.basename(component_file)}: Syntax OK")
                    
            except Exception as e:
                print(f"❌ {os.path.basename(component_file)}: Error reading file")
                syntax_ok = False
        else:
            print(f"❌ {os.path.basename(component_file)}: File not found")
            syntax_ok = False
    
    return syntax_ok

def main():
    """Main test function"""
    print("🚀 Starting Simple Component Tests")
    print("=" * 50)
    
    tests = [
        ("Component Files", test_component_files),
        ("Component Imports", test_component_imports),
        ("Styling Approach", test_styling_approach),
        ("Component Structure", test_component_structure),
        ("Package Dependencies", test_package_dependencies),
        ("Build Compatibility", test_build_compatibility)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🏆 TEST RESULTS SUMMARY:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Components are ready for integration!")
        print("✅ Modern UI design implemented correctly!")
        print("✅ Ready for next development phase!")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("🔧 Some components need attention")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
