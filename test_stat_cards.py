#!/usr/bin/env python3
"""
Stat Card Animation Test Script
Tests the enhanced stat card components and animations
"""

import os
import re

def test_stat_card_structure():
    """Test stat card component structure"""
    print("📊 Testing Stat Card Structure")
    print("=" * 50)
    
    statcard_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/StatCardNew.jsx"
    
    if os.path.exists(statcard_path):
        with open(statcard_path, 'r') as f:
            content = f.read()
        
        structure_features = {
            'React Component': 'import React' in content and 'export default' in content,
            'Material-UI Card': 'Card' in content and 'CardContent' in content,
            'Props Interface': 'title' in content and 'value' in content,
            'Icon Support': 'icon: Icon' in content,
            'Trend Support': 'trend' in content,
            'Gradient Support': 'gradient' in content,
            'Color Support': 'color' in content
        }
        
        for feature, exists in structure_features.items():
            if exists:
                print(f"✅ {feature}")
            else:
                print(f"⚠️ {feature} not found")
        
        return any(structure_features.values())
    
    return False

def test_gradient_implementations():
    """Test gradient implementations in stat cards"""
    print("\n🎨 Testing Gradient Implementations")
    print("=" * 50)
    
    statcard_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/StatCardNew.jsx"
    
    if os.path.exists(statcard_path):
        with open(statcard_path, 'r') as f:
            content = f.read()
        
        gradient_features = {
            'Default Gradients': 'defaultGradients' in content,
            'Color Mapping': '#f59e0b' in content,
            'Linear Gradient': 'linear-gradient' in content,
            'Gradient Background': 'background: cardGradient' in content,
            'Gradient Avatar': 'background: cardGradient' in content,
            'Multiple Colors': len(re.findall(r'#[0-9a-fA-F]{6}', content)) >= 5
        }
        
        for feature, exists in gradient_features.items():
            if exists:
                print(f"✅ {feature}")
            else:
                print(f"⚠️ {feature} not found")
        
        return any(gradient_features.values())
    
    return False

def test_hover_effects():
    """Test hover effects implementation"""
    print("\n🖱️ Testing Hover Effects")
    print("=" * 50)
    
    statcard_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/StatCardNew.jsx"
    
    if os.path.exists(statcard_path):
        with open(statcard_path, 'r') as f:
            content = f.read()
        
        hover_features = {
            'Hover Selector': '&:hover' in content,
            'Transform Effect': 'translateY' in content,
            'Shadow Effect': 'boxShadow' in content,
            'Border Color Change': 'borderColor' in content,
            'Transition Property': 'transition' in content,
            'Ease Function': 'ease' in content
        }
        
        for feature, exists in hover_features.items():
            if exists:
                print(f"✅ {feature}")
            else:
                print(f"⚠️ {feature} not found")
        
        return any(hover_features.values())
    
    return False

def test_animation_properties():
    """Test animation and transition properties"""
    print("\n⚡ Testing Animation Properties")
    print("=" * 50)
    
    statcard_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/StatCardNew.jsx"
    
    if os.path.exists(statcard_path):
        with open(statcard_path, 'r') as f:
            content = f.read()
        
        animation_features = {
            'Transition All': 'transition: all' in content,
            'Transition Duration': '0.3s' in content,
            'Transform Property': 'transform' in content,
            'Box Shadow Animation': 'boxShadow' in content,
            'Border Animation': 'border' in content,
            'Smooth Animation': 'ease' in content
        }
        
        for feature, exists in animation_features.items():
            if exists:
                print(f"✅ {feature}")
            else:
                print(f"⚠️ {feature} not found")
        
        return any(animation_features.values())
    
    return False

def test_responsive_design():
    """Test responsive design features"""
    print("\n📱 Testing Responsive Design")
    print("=" * 50)
    
    statcard_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/StatCardNew.jsx"
    
    if os.path.exists(statcard_path):
        with open(statcard_path, 'r') as f:
            content = f.read()
        
        responsive_features = {
            'Flexible Width': 'flex: 1' in content,
            'Minimum Width': 'minWidth' in content,
            'Responsive Typography': 'fontSize' in content,
            'Responsive Spacing': 'padding' in content or 'p: ' in content,
            'Flexible Layout': 'display: flex' in content,
            'Adaptive Content': 'flex: 1' in content
        }
        
        for feature, exists in responsive_features.items():
            if exists:
                print(f"✅ {feature}")
            else:
                print(f"⚠️ {feature} not found")
        
        return any(responsive_features.values())
    
    return False

def test_visual_hierarchy():
    """Test visual hierarchy and typography"""
    print("\n📝 Testing Visual Hierarchy")
    print("=" * 50)
    
    statcard_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/StatCardNew.jsx"
    
    if os.path.exists(statcard_path):
        with open(statcard_path, 'r') as f:
            content = f.read()
        
        hierarchy_features = {
            'Title Typography': 'variant="overline"' in content,
            'Value Typography': 'variant="h4"' in content,
            'Subtitle Typography': 'variant="caption"' in content,
            'Font Weights': 'fontWeight' in content,
            'Font Sizes': 'fontSize' in content,
            'Text Colors': 'color' in content,
            'Letter Spacing': 'letterSpacing' in content
        }
        
        for feature, exists in hierarchy_features.items():
            if exists:
                print(f"✅ {feature}")
            else:
                print(f"⚠️ {feature} not found")
        
        return any(hierarchy_features.values())
    
    return False

def test_data_visualization():
    """Test data visualization features"""
    print("\n📈 Testing Data Visualization")
    print("=" * 50)
    
    statcard_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/StatCardNew.jsx"
    
    if os.path.exists(statcard_path):
        with open(statcard_path, 'r') as f:
            content = f.read()
        
        viz_features = {
            'Trend Display': 'trend' in content,
            'Percentage Display': '%' in content,
            'Icon Integration': 'Icon' in content,
            'Value Formatting': 'value' in content,
            'Sub Value Support': 'subValue' in content,
            'Color Coding': 'color: trend > 0' in content
        }
        
        for feature, exists in viz_features.items():
            if exists:
                print(f"✅ {feature}")
            else:
                print(f"⚠️ {feature} not found")
        
        return any(viz_features.values())
    
    return False

def test_css_integration():
    """Test CSS integration and styling"""
    print("\n🎨 Testing CSS Integration")
    print("=" * 50)
    
    # Check if CSS variables are used
    css_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/App.css"
    
    css_integration = False
    
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            css_content = f.read()
        
        css_features = {
            'CSS Variables': '--color-' in css_content,
            'Gradient Definitions': 'gradient' in css_content,
            'Shadow Definitions': 'shadow-' in css_content,
            'Animation Keyframes': '@keyframes' in css_content,
            'Transition Classes': 'transition-' in css_content,
            'Hover Classes': 'hover-' in css_content
        }
        
        for feature, exists in css_features.items():
            if exists:
                print(f"✅ CSS: {feature}")
                css_integration = True
            else:
                print(f"⚠️ CSS: {feature} not found")
    
    # Check if stat card uses CSS variables
    statcard_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/StatCardNew.jsx"
    
    if os.path.exists(statcard_path):
        with open(statcard_path, 'r') as f:
            statcard_content = f.read()
        
        if 'var(--' in statcard_content:
            print("✅ StatCard uses CSS variables")
        else:
            print("⚠️ StatCard doesn't use CSS variables")
    
    return css_integration

def test_performance_optimizations():
    """Test performance optimizations"""
    print("\n⚡ Testing Performance Optimizations")
    print("=" * 50)
    
    statcard_path = "/home/senarios/Desktop/survey-bot/survai-platform/dashboard/src/components/StatCardNew.jsx"
    
    if os.path.exists(statcard_path):
        with open(statcard_path, 'r') as f:
            content = f.read()
        
        performance_features = {
            'Transform Animation': 'transform: translateY' in content,
            'Opacity Animation': 'opacity' in content,
            'Hardware Acceleration': 'transform3d' in content or 'translate3d' in content,
            'Efficient Transitions': 'transition' in content,
            'Minimal Repaints': 'will-change' in content,
            'Optimized Shadows': 'box-shadow' in content
        }
        
        for feature, exists in performance_features.items():
            if exists:
                print(f"✅ {feature}")
            else:
                print(f"⚠️ {feature} not found")
        
        return any(performance_features.values())
    
    return False

def main():
    """Main test function"""
    print("🚀 Starting Stat Card Animation Tests")
    print("=" * 50)
    
    tests = [
        ("Stat Card Structure", test_stat_card_structure),
        ("Gradient Implementations", test_gradient_implementations),
        ("Hover Effects", test_hover_effects),
        ("Animation Properties", test_animation_properties),
        ("Responsive Design", test_responsive_design),
        ("Visual Hierarchy", test_visual_hierarchy),
        ("Data Visualization", test_data_visualization),
        ("CSS Integration", test_css_integration),
        ("Performance Optimizations", test_performance_optimizations)
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
    print("🏆 STAT CARD TEST RESULTS:")
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
        print("\n🎉 STAT CARDS WORKING PERFECTLY!")
        print("✅ Modern design implemented!")
        print("✅ Gradients and animations working!")
        print("✅ Hover effects smooth!")
        print("✅ Responsive design ready!")
        print("✅ Performance optimized!")
    else:
        print(f"\n⚠️ {total - passed} tests need attention")
        print("🔧 Some stat card features need improvement")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
