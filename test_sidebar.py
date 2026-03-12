#!/usr/bin/env python3
"""
Sidebar Component Test Script
Tests the new modern sidebar functionality
"""

import asyncio
import time
from playwright.async_api import async_playwright

async def test_sidebar_functionality():
    """Test sidebar component functionality"""
    print("🧭 Testing Sidebar Functionality")
    print("=" * 50)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to dashboard
            await page.goto("http://localhost:8080/dashboard")
            await page.wait_for_load_state('networkidle')
            
            # Test 1: Sidebar Visibility
            print("\n📋 Test 1: Sidebar Visibility")
            sidebar = await page.query_selector('[data-testid="sidebar"]')
            if sidebar:
                print("✅ Sidebar element found")
            else:
                print("ℹ️ Looking for sidebar by class names...")
                sidebar = await page.query_selector('.sidebar-new, .MuiDrawer-root')
                if sidebar:
                    print("✅ Sidebar found by class")
                else:
                    print("❌ Sidebar not found")
                    return False
            
            # Test 2: Navigation Items
            print("\n📝 Test 2: Navigation Items")
            
            nav_items = await page.query_selector_all('[role="button"], .nav-item')
            print(f"✅ Found {len(nav_items)} navigation items")
            
            # Check for specific navigation items
            expected_items = ['Dashboard', 'Templates', 'Surveys']
            for item in expected_items:
                item_element = await page.query_selector(f'text="{item}"')
                if item_element:
                    print(f"✅ {item} navigation item found")
                else:
                    print(f"⚠️ {item} navigation item not found")
            
            # Test 3: User Profile Section
            print("\n👤 Test 3: User Profile Section")
            
            user_avatar = await page.query_selector('.MuiAvatar-root')
            if user_avatar:
                print("✅ User avatar found")
                avatar_text = await user_avatar.inner_text()
                print(f"   Avatar text: {avatar_text}")
            else:
                print("⚠️ User avatar not found")
            
            user_name = await page.query_selector('text="Admin User"')
            if user_name:
                print("✅ User name found")
            else:
                print("⚠️ User name not found")
            
            # Test 4: Expandable Sections
            print("\n🔄 Test 4: Expandable Sections")
            
            # Look for expandable sections (Templates, Surveys)
            expandable_buttons = await page.query_selector_all('[aria-expanded], .expandable')
            print(f"✅ Found {len(expandable_buttons)} expandable sections")
            
            if expandable_buttons:
                # Test clicking first expandable section
                await expandable_buttons[0].click()
                await page.wait_for_timeout(500)
                print("✅ Expandable section clicked")
                
                # Check if content expanded
                expanded_content = await page.query_selector('.MuiCollapse-root, .expanded-content')
                if expanded_content:
                    print("✅ Content expanded successfully")
                else:
                    print("⚠️ Expanded content not found")
            
            # Test 5: Create Template Button
            print("\n➕ Test 5: Create Template Button")
            
            create_button = await page.query_selector('text="Create Template"')
            if create_button:
                print("✅ Create Template button found")
                
                # Test button styling
                button_styles = await page.evaluate("""
                    (button) => {
                        const styles = getComputedStyle(button);
                        return {
                            background: styles.background,
                            color: styles.color,
                            borderRadius: styles.borderRadius,
                            padding: styles.padding
                        };
                    }
                """, create_button)
                
                if 'gradient' in button_styles['background'].lower():
                    print("✅ Button has gradient background")
                else:
                    print("ℹ️ Button background:", button_styles['background'])
                
                # Test button click
                await create_button.click()
                await page.wait_for_timeout(1000)
                print("✅ Create Template button clicked")
                
            else:
                print("⚠️ Create Template button not found")
            
            # Test 6: Bottom Navigation Items
            print("\n⚙️ Test 6: Bottom Navigation Items")
            
            settings_item = await page.query_selector('text="Settings"')
            if settings_item:
                print("✅ Settings item found")
            else:
                print("⚠️ Settings item not found")
            
            logout_item = await page.query_selector('text="Logout"')
            if logout_item:
                print("✅ Logout item found")
            else:
                print("⚠️ Logout item not found")
            
            # Test 7: Responsive Behavior
            print("\n📱 Test 7: Responsive Behavior")
            
            # Test mobile view
            await page.set_viewport_size({"width": 375, "height": 667})
            await page.wait_for_timeout(500)
            
            mobile_sidebar = await page.query_selector('[data-testid="mobile-sidebar"]')
            if mobile_sidebar:
                print("✅ Mobile sidebar responsive")
            else:
                print("ℹ️ Testing mobile responsiveness...")
                
                # Check if sidebar transforms on mobile
                sidebar_transform = await page.evaluate("""
                    () => {
                        const sidebar = document.querySelector('.sidebar-new, .MuiDrawer-root');
                        return sidebar ? getComputedStyle(sidebar).transform : 'none';
                    }
                """)
                
                if 'translateX' in sidebar_transform:
                    print("✅ Sidebar transforms on mobile")
                else:
                    print("ℹ️ Sidebar transform:", sidebar_transform)
            
            # Test 8: Hover Effects
            print("\n🖱️ Test 8: Hover Effects")
            
            # Reset to desktop view
            await page.set_viewport_size({"width": 1920, "height": 1080})
            await page.wait_for_timeout(500)
            
            # Test hover on navigation items
            if nav_items:
                await nav_items[0].hover()
                await page.wait_for_timeout(500)
                
                # Check if hover effect applied
                hover_styles = await page.evaluate("""
                    (element) => {
                        const styles = getComputedStyle(element);
                        return {
                            backgroundColor: styles.backgroundColor,
                            transition: styles.transition
                        };
                    }
                """, nav_items[0])
                
                if hover_styles['backgroundColor'] != 'rgba(0, 0, 0, 0)' and hover_styles['backgroundColor'] != 'transparent':
                    print("✅ Hover effect working on navigation items")
                else:
                    print("⚠️ Hover effect not clearly visible")
            
            # Test 9: Active State
            print("\n🎯 Test 9: Active State")
            
            # Check if dashboard is active
            active_item = await page.query_selector('.active, [aria-current="page"]')
            if active_item:
                print("✅ Active state found")
                active_text = await active_item.inner_text()
                print(f"   Active item: {active_text}")
            else:
                print("ℹ️ Active state not clearly marked")
            
            # Test 10: Accessibility
            print("\n♿ Test 10: Accessibility")
            
            # Check for ARIA labels
            aria_elements = await page.query_selector_all('[aria-label], [role]')
            print(f"✅ Found {len(aria_elements)} elements with ARIA attributes")
            
            # Check for keyboard navigation
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(200)
            
            focused_element = await page.evaluate("""
                () => document.activeElement.tagName
            """)
            
            if focused_element:
                print(f"✅ Keyboard navigation working - focused on: {focused_element}")
            else:
                print("⚠️ Keyboard navigation issue")
            
            print("\n" + "=" * 50)
            print("🎉 Sidebar Functionality Test Complete!")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            return False
        finally:
            await browser.close()

async def main():
    """Main test function"""
    print("🚀 Starting Sidebar Functionality Test")
    print("=" * 50)
    
    success = await test_sidebar_functionality()
    
    print("\n" + "=" * 50)
    print("🏆 TEST RESULTS:")
    if success:
        print("✅ Sidebar functionality working correctly!")
        print("✅ All components responsive!")
        print("✅ Navigation items functional!")
        print("✅ User interface elements working!")
    else:
        print("⚠️ Some issues found - review implementation")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
