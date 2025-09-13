import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def main():
    print("🚀 Starting Selenium test with your profile...")
    
    # Check if profile picture exists (verifies it's a real user profile)
    profile_picture_path = '/home/runner/my_google_profile/google-chrome/Default/Google Profile Picture.png'
    if os.path.exists(profile_picture_path):
        print("✅ Google Profile Picture found - this is a real user profile")
    else:
        print("❌ Google Profile Picture missing - profile may be incomplete")
        # List what files we actually have
        profile_dir = '/home/runner/my_google_profile/google-chrome/Default/'
        if os.path.exists(profile_dir):
            print("📁 Files in profile directory:")
            for f in os.listdir(profile_dir)[:10]:  # Show first 10 files
                print(f"   - {f}")
    
    # Configure Chrome options for GitHub Actions
    chrome_options = Options()
    
    # Use the correct profile path
    profile_path = '/home/runner/my_google_profile/google-chrome'
    chrome_options.add_argument(f'--user-data-dir={profile_path}')
    chrome_options.add_argument('--profile-directory=Default')
    
    # Required for GitHub Actions
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920x1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--remote-debugging-port=0')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # Initialize the driver
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Chrome driver initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize Chrome driver: {e}")
        return

    def check_running_cells():
        """Check if there are any running Colab cells"""
        running_indicators = [
            "//div[contains(@class, 'running')]",
            "//div[contains(@class, 'spinner')]",
            "//div[contains(@class, 'progress')]",
            "//div[contains(@class, 'executing')]",
            "//*[contains(text(), 'Executing')]",
            "//*[contains(text(), 'Running')]",
        ]
        
        for indicator in running_indicators:
            try:
                elements = driver.find_elements(By.XPATH, indicator)
                if elements:
                    print(f"   ⚡ Found {len(elements)} running cell indicators")
                    return True
            except:
                continue
        return False

    try:
        # Visit the specified Google Colab URL
        print("\n🌐 Visiting Google Colab URL...")
        colab_url = "https://colab.research.google.com/drive/1MElDzVC3JbJ8zLmf5AMQp54mi_u3Uu7r"
        driver.get(colab_url)
        
        # Wait for page to load
        print("⏳ Waiting for page to load...")
        time.sleep(10)

        # Check if we're on the right page
        print(f"📄 Current URL: {driver.current_url}")
        print(f"📄 Page title: {driver.title}")

        # Check if we're logged in (should not be on login page)
        if "signin" in driver.current_url or "accounts.google.com" in driver.current_url:
            print("❌ NOT LOGGED IN: Redirected to login page")
            print("   The session cookies may be expired or invalid")
            
            # Let's try to check what cookies we actually have
            try:
                cookies = driver.get_cookies()
                print(f"   🍪 Found {len(cookies)} cookies in the profile")
                for cookie in cookies[:5]:  # Show first 5 cookies
                    print(f"     - {cookie['name']}: {cookie.get('value', '')[:50]}...")
            except:
                print("   ❓ Could not retrieve cookies")
            
            return

        # If we get here, we're logged in!
        print("✅ SUCCESS: Logged in and on Colab page!")
        
        # Check if there are any running Colab cells
        print("🔍 Checking for running Colab cells...")
        
        cell_running = check_running_cells()
        
        if cell_running:
            print("   ⏳ Cells are running - waiting for completion...")
            time.sleep(15)
        else:
            print("   ✅ No running cells detected")

        # Take screenshot
        screenshot_filename = 'colab_screenshot.png'
        driver.save_screenshot(screenshot_filename)
        print(f"   📸 Screenshot saved: {screenshot_filename}")

        print("\n🎯 SCREENSHOT COMPLETE")
        print(f"📋 URL visited: {colab_url}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # Always quit the driver
        try:
            driver.quit()
            print("\n✅ Browser closed. Test completed.")
        except:
            print("\n⚠️  Browser already closed or failed to quit.")

if __name__ == "__main__":
    main()
