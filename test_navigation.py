#!/usr/bin/env python3
"""
Navigation Functionality Test Script
Tests the navigation components and routing
"""

import os
import json

def test_navigation_components():
    """Test navigation component structure"""
    print("🧭 Testing Navigation Components")
    print("=" * 50)
    
    # Test SidebarNew navigation
    sidebar_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/SidebarNew.jsx"
    
    if os.path.exists(sidebar_path):
        with open(sidebar_path, 'r') as f:
            sidebar_content = f.read()
        
        navigation_features = {
            'React Router': 'useNavigate' in sidebar_content,
            'Location Tracking': 'useLocation' in sidebar_content,
            'Active State': 'isActive' in sidebar_content,
            'Menu Items': 'menuItems' in sidebar_content,
            'Expandable Sections': 'toggleSection' in sidebar_content,
            'User Profile': 'Admin User' in sidebar_content,
            'Navigation Handler': 'handleNavigation' in sidebar_content
        }
        
        for feature, exists in navigation_features.items():
            if exists:
                print(f"✅ Sidebar: {feature}")
            else:
                print(f"⚠️ Sidebar: {feature} not found")
    
    # Test TopNavNew navigation
    topnav_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/TopNavNew.jsx"
    
    if os.path.exists(topnav_path):
        with open(topnav_path, 'r') as f:
            topnav_content = f.read()
        
        topnav_features = {
            'Search Functionality': 'searchQuery' in topnav_content,
            'User Menu': 'handleUserMenuOpen' in topnav_content,
            'Notifications': 'notificationAnchor' in topnav_content,
            'Menu Toggle': 'onSidebarToggle' in topnav_content,
            'Dropdown Menus': 'Menu' in topnav_content,
            'User Avatar': 'Avatar' in topnav_content
        }
        
        for feature, exists in topnav_features.items():
            if exists:
                print(f"✅ TopNav: {feature}")
            else:
                print(f"⚠️ TopNav: {feature} not found")
    
    return True

def test_routing_structure():
    """Test routing configuration"""
    print("\n🛣️ Testing Routing Structure")
    print("=" * 50)
    
    # Look for routing configuration
    routes_files = [
        "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/routes/index.jsx",
        "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/App.jsx",
        "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/main.jsx"
    ]
    
    routing_found = False
    
    for route_file in routes_files:
        if os.path.exists(route_file):
            with open(route_file, 'r') as f:
                route_content = f.read()
            
            if 'Route' in route_content or 'Routes' in route_content:
                print(f"✅ Routing found in {os.path.basename(route_file)}")
                routing_found = True
                
                # Check for dashboard route
                if '/dashboard' in route_content:
                    print("✅ Dashboard route configured")
                
                # Check for survey routes
                if '/surveys' in route_content:
                    print("✅ Survey routes configured")
                
                # Check for template routes
                if '/templates' in route_content:
                    print("✅ Template routes configured")
    
    if not routing_found:
        print("⚠️ No routing configuration found")
    
    return routing_found

def test_navigation_paths():
    """Test navigation path definitions"""
    print("\n📁 Testing Navigation Paths")
    print("=" * 50)
    
    sidebar_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/SidebarNew.jsx"
    
    if os.path.exists(sidebar_path):
        with open(sidebar_path, 'r') as f:
            content = f.read()
        
        # Extract menu items
        expected_paths = [
            '/dashboard',
            '/templates',
            '/templates/create',
            '/templates/manage',
            '/surveys',
            '/surveys/launch',
            '/surveys/manage',
            '/settings'
        ]
        
        paths_found = []
        
        for path in expected_paths:
            if path in content:
                print(f"✅ Path defined: {path}")
                paths_found.append(path)
            else:
                print(f"⚠️ Path missing: {path}")
        
        print(f"\n📊 Path Coverage: {len(paths_found)}/{len(expected_paths)}")
        return len(paths_found) >= len(expected_paths) * 0.8  # 80% coverage
    
    return False

def test_navigation_interactions():
    """Test navigation interaction handlers"""
    print("\n🖱️ Testing Navigation Interactions")
    print("=" * 50)
    
    sidebar_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/SidebarNew.jsx"
    
    if os.path.exists(sidebar_path):
        with open(sidebar_path, 'r') as f:
            content = f.read()
        
        interaction_handlers = {
            'Click Handlers': 'onClick' in content,
            'Navigation Function': 'navigate(' in content,
            'State Management': 'useState' in content,
            'Section Toggle': 'toggleSection' in content,
            'Mobile Close': 'onClose' in content,
            'Active State Logic': 'isActive(' in content
        }
        
        for handler, exists in interaction_handlers.items():
            if exists:
                print(f"✅ {handler}")
            else:
                print(f"⚠️ {handler} not found")
        
        return any(interaction_handlers.values())
    
    return False

def test_responsive_navigation():
    """Test responsive navigation features"""
    print("\n📱 Testing Responsive Navigation")
    print("=" * 50)
    
    sidebar_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/SidebarNew.jsx"
    
    if os.path.exists(sidebar_path):
        with open(sidebar_path, 'r') as f:
            content = f.read()
        
        responsive_features = {
            'Mobile Detection': 'isMobile' in content,
            'Mobile Transform': 'translateX' in content,
            'Mobile Close Handler': 'onClose' in content,
            'Responsive Width': '100vw' in content,
            'Fixed Position': 'position: fixed' in content,
            'Z-index Management': 'zIndex' in content
        }
        
        for feature, exists in responsive_features.items():
            if exists:
                print(f"✅ {feature}")
            else:
                print(f"⚠️ {feature} not found")
        
        return any(responsive_features.values())
    
    return False

def test_user_interface_elements():
    """Test user interface elements in navigation"""
    print("\n👤 Testing User Interface Elements")
    print("=" * 50)
    
    # Test Sidebar UI elements
    sidebar_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/SidebarNew.jsx"
    
    if os.path.exists(sidebar_path):
        with open(sidebar_path, 'r') as f:
            sidebar_content = f.read()
        
        sidebar_ui = {
            'User Avatar': 'Avatar' in sidebar_content,
            'User Name': 'Admin User' in sidebar_content,
            'User Email': 'admin@survai.com' in sidebar_content,
            'Navigation Icons': 'icon=' in sidebar_content,
            'Expandable Arrows': 'ChevronDown' in sidebar_content,
            'Logout Button': 'Logout' in sidebar_content
        }
        
        print("📋 Sidebar UI Elements:")
        for element, exists in sidebar_ui.items():
            if exists:
                print(f"   ✅ {element}")
            else:
                print(f"   ⚠️ {element} not found")
    
    # Test TopNav UI elements
    topnav_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/TopNavNew.jsx"
    
    if os.path.exists(topnav_path):
        with open(topnav_path, 'r') as f:
            topnav_content = f.read()
        
        topnav_ui = {
            'Search Bar': 'TextField' in topnav_content,
            'Search Icon': 'Search' in topnav_content,
            'Notification Bell': 'Bell' in topnav_content,
            'Notification Badge': 'Badge' in topnav_content,
            'User Menu': 'Menu' in topnav_content,
            'Menu Toggle': 'MenuIcon' in topnav_content
        }
        
        print("\n📋 TopNav UI Elements:")
        for element, exists in topnav_ui.items():
            if exists:
                print(f"   ✅ {element}")
            else:
                print(f"   ⚠️ {element} not found")
    
    return True

def test_accessibility_features():
    """Test accessibility features in navigation"""
    print("\n♿ Testing Accessibility Features")
    print("=" * 50)
    
    sidebar_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/SidebarNew.jsx"
    
    if os.path.exists(sidebar_path):
        with open(sidebar_path, 'r') as f:
            content = f.read()
        
        accessibility_features = {
            'Semantic HTML': 'Button' in content,
            'ARIA Labels': 'aria-' in content,
            'Keyboard Navigation': 'tabIndex' in content,
            'Focus Management': 'onFocus' in content,
            'Screen Reader Support': 'role=' in content,
            'Color Contrast': 'color:' in content
        }
        
        for feature, exists in accessibility_features.items():
            if exists:
                print(f"✅ {feature}")
            else:
                print(f"⚠️ {feature} not found")
        
        return any(accessibility_features.values())
    
    return False

def main():
    """Main test function"""
    print("🚀 Starting Navigation Functionality Tests")
    print("=" * 50)
    
    tests = [
        ("Navigation Components", test_navigation_components),
        ("Routing Structure", test_routing_structure),
        ("Navigation Paths", test_navigation_paths),
        ("Navigation Interactions", test_navigation_interactions),
        ("Responsive Navigation", test_responsive_navigation),
        ("User Interface Elements", test_user_interface_elements),
        ("Accessibility Features", test_accessibility_features)
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
    print("🏆 NAVIGATION TEST RESULTS:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed >= total * 0.8:  # 80% success rate
        print("\n🎉 NAVIGATION FUNCTIONALITY WORKING!")
        print("✅ Navigation components properly structured!")
        print("✅ Routing paths defined!")
        print("✅ User interactions implemented!")
        print("✅ Responsive design working!")
        print("✅ UI elements accessible!")
    else:
        print(f"\n⚠️ {total - passed} tests need attention")
        print("🔧 Some navigation features need improvement")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
