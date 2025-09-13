import time
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def main():
    print("🚀 Starting Selenium test with your profile...")
    
    # === FIX: Clean up any existing Chrome processes and lock files ===
    print("🧹 Cleaning up any existing Chrome processes...")
    os.system('pkill -f chrome || true')  # Kill any Chrome processes
    os.system('pkill -f chromedriver || true')  # Kill any ChromeDriver processes
    
    # Define the profile path
    profile_path = '/home/runner/.config/google-chrome'
    
    # Remove Chrome lock files if they exist
    lock_files = [
        os.path.join(profile_path, 'Default', 'SingletonLock'),
        os.path.join(profile_path, 'SingletonLock'),
        os.path.join(profile_path, 'SingletonCookie'),
        os.path.join(profile_path, 'Default', 'SingletonCookie')
    ]
    
    for lock_file in lock_files:
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
                print(f"✅ Removed lock file: {lock_file}")
            except Exception as e:
                print(f"⚠️  Could not remove {lock_file}: {e}")
    
    # Configure Chrome options for GitHub Actions
    chrome_options = Options()
    
    # === CRITICAL: Use the injected profile path ===
    chrome_options.add_argument(f'--user-data-dir={profile_path}')
    chrome_options.add_argument('--profile-directory=Default')
    
    # === FIX: Add unique user data directory per run ===
    import uuid
    unique_id = uuid.uuid4().hex[:8]
    unique_profile_dir = f'{profile_path}_{unique_id}'
    
    # Copy profile to unique directory to avoid conflicts
    if os.path.exists(profile_path):
        try:
            shutil.copytree(profile_path, unique_profile_dir)
            print(f"✅ Copied profile to unique directory: {unique_profile_dir}")
            chrome_options.add_argument(f'--user-data-dir={unique_profile_dir}')
        except Exception as e:
            print(f"⚠️  Could not copy profile, using original: {e}")
            chrome_options.add_argument(f'--user-data-dir={profile_path}')
    
    # Chrome configuration
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--remote-debugging-port=0')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Additional stability arguments
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-notifications')

    # Initialize the driver
    try:
        print("🛠️  Setting up ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome driver initialized successfully!")
        
    except WebDriverException as e:
        print(f"❌ Failed to initialize Chrome driver: {e}")
        print("🔄 Trying alternative method without service...")
        try:
            driver = webdriver.Chrome(options=chrome_options)
            print("✅ Chrome driver initialized with fallback method!")
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
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

    def run_focused_cell():
        """Run the currently focused cell using Ctrl+Enter"""
        print("   ⌨️  Sending Ctrl+Enter to run focused cell...")
        
        try:
            body = driver.find_element(By.TAG_NAME, 'body')
            body.send_keys(Keys.CONTROL + Keys.ENTER)
            print("   ✅ Ctrl+Enter sent successfully!")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to send Ctrl+Enter: {str(e)}")
            return False

    def focus_first_cell():
        """Try to focus on the first code cell"""
        print("   🔍 Attempting to focus on first code cell...")
        
        cell_selectors = [
            "//div[contains(@class, 'code-cell')]",
            "//div[contains(@class, 'cell')]",
            "//div[contains(@class, 'input')]",
            "//div[@role='textbox']",
        ]
        
        for selector in cell_selectors:
            try:
                cells = driver.find_elements(By.XPATH, selector)
                if cells:
                    print(f"   ✅ Found {len(cells)} potential code cells")
                    cells[0].click()
                    print("   🎯 First code cell focused!")
                    return True
            except Exception as e:
                continue
        
        print("   ⚠️  Could not find a code cell to focus")
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

        # Check if there are any running Colab cells
        print("🔍 Checking for running Colab cells...")
        
        cell_running = check_running_cells()
        cell_started = False
        
        if cell_running:
            print("   ⏳ Cells are running - waiting for completion...")
            time.sleep(15)
        else:
            print("   ✅ No running cells detected - attempting to run first cell")
            
            if focus_first_cell():
                time.sleep(2)
            
            cell_started = run_focused_cell()
            
            if cell_started:
                print("   ⏳ Waiting for cell to start running...")
                time.sleep(10)

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
        
        # Clean up temporary profile directory
        if 'unique_profile_dir' in locals() and os.path.exists(unique_profile_dir):
            try:
                shutil.rmtree(unique_profile_dir)
                print(f"✅ Cleaned up temporary profile: {unique_profile_dir}")
            except:
                print("⚠️  Could not clean up temporary profile")

if __name__ == "__main__":
    main()
