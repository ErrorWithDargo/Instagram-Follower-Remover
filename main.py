import tkinter as tk
from tkinter import messagebox
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

class InstaRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Follower Remover")
        self.root.geometry("400x500")
        self.driver = None
        self.is_running = False

        # GUI Components
        self.label_limit = tk.Label(root, text="Number of followers to remove:")
        self.label_limit.pack(pady=(10, 0))

        self.entry_limit = tk.Entry(root)
        self.entry_limit.insert(0, "1000")
        self.entry_limit.pack(pady=5)

        self.label_user = tk.Label(root, text="Your Instagram Username:")
        self.label_user.pack(pady=(10, 0))

        self.entry_user = tk.Entry(root)
        self.entry_user.pack(pady=5)

        self.btn_open_browser = tk.Button(root, text="1. Open Browser & Login Manually", command=self.open_browser, bg="#4CAF50", fg="white")
        self.btn_open_browser.pack(pady=20, fill='x', padx=50)

        self.label_status = tk.Label(root, text="Status: Waiting to start", fg="gray")
        self.label_status.pack(pady=10)

        self.btn_start = tk.Button(root, text="2. Start Removing", command=self.start_removal_thread, state=tk.DISABLED, bg="#2196F3", fg="white")
        self.btn_start.pack(pady=10, fill='x', padx=50)
        
        self.btn_stop = tk.Button(root, text="Stop", command=self.stop_removal, state=tk.DISABLED, bg="#f44336", fg="white")
        self.btn_stop.pack(pady=10, fill='x', padx=50)

        self.log_text = tk.Text(root, height=10, width=40, state=tk.DISABLED)
        self.log_text.pack(pady=10,padx=10)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.label_status.config(text=f"Status: {message}")

    def open_browser(self):
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service)
            self.driver.get("https://www.instagram.com/accounts/login/")
            self.log("Browser opened. Please Log in manually.")
            self.btn_start.config(state=tk.NORMAL)
            self.btn_open_browser.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open browser: {e}")

    def start_removal_thread(self):
        if not self.driver:
            messagebox.showwarning("Warning", "Browser not open!")
            return
        
        limit_str = self.entry_limit.get()
        if not limit_str.isdigit():
            messagebox.showerror("Error", "Please enter a valid number.")
            return
        
        self.limit = int(limit_str)
        self.username = self.entry_user.get().strip()

        if not self.username:
            messagebox.showwarning("Warning", "Please enter your username!")
            return

        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        
        threading.Thread(target=self.remove_followers).start()

    def remove_followers(self):
        try:
            self.log("Starting removal process...")
            
            # Navigate to profile

            if self.username:
                self.log(f"Navigating to {self.username}'s profile...")
                self.driver.get(f"https://www.instagram.com/{self.username}/")
                time.sleep(3)
            
            # Check if we see "Followers" link

            # Check if we see "Followers" link
            try:
                # Wait a bit for user to be ready
                time.sleep(2)
                
                # Look for "followers" link. It usually has "followers" in href or text.
                followers_link = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "followers"))
                )
                followers_link.click()
                self.log("Clicked Followers link.")
            except Exception:
                self.log("Could not find 'followers' link. Please navigate to your profile and click 'Followers' manually, then generic wait.")
                time.sleep(5) # Give user time if they haven't

            # Now we are in the followers modal/page
            removed_count = 0
            
            # Wait for list to load
            time.sleep(3)

            while removed_count < self.limit and self.is_running:
                try:
                    # Generic strategy: Find any button that looks like a "Remove" button
                    # We try multiple selectors
                    possible_buttons = []
                    
                    # 1. Standard button with text 'Remove'
                    possible_buttons.extend(self.driver.find_elements(By.XPATH, "//button[text()='Remove']"))
                    
                    # 2. Button containing text 'Remove'
                    if not possible_buttons:
                         possible_buttons.extend(self.driver.find_elements(By.XPATH, "//button[contains(., 'Remove')]"))
                    
                    # 3. Div acting as button
                    if not possible_buttons:
                         possible_buttons.extend(self.driver.find_elements(By.XPATH, "//div[@role='button'][text()='Remove']"))

                    if not possible_buttons:
                        self.log("No 'Remove' buttons found. Scrolling...")
                        
                        # scrolling logic
                        try:
                            # Try to find the scrollable modal dialog
                            dialog = self.driver.find_element(By.XPATH, "//div[@role='dialog']//div[@style and contains(@style, 'height')]")
                            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
                        except:
                             # Fallback: try to scroll the very last div in dialog
                             try:
                                 dialog = self.driver.find_element(By.XPATH, "//div[@role='dialog']//div[contains(@class, 'x7r02ix')]") 
                                 self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
                             except:
                                 self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        
                        time.sleep(2)
                        continue

                    # Filter visible buttons
                    btn = None
                    for b in possible_buttons:
                        if b.is_displayed():
                            btn = b
                            break
                    
                    if not btn:
                        self.log("Found buttons but none are visible. Scrolling...")
                        time.sleep(1)
                        continue

                    btn.click()
                    
                    # Wait for confirmation modal
                    time.sleep(1.5)
                    
                    # Click confirm "Remove" (usually red or secondary confirmation)
                    try:
                        confirm_btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[@role='dialog']//button[text()='Remove']"))
                        )
                        confirm_btn.click()
                    except:
                        # Sometimes text might be different or nested
                        confirm_btn = self.driver.find_element(By.XPATH, "//div[@role='dialog']//button[contains(., 'Remove')]")
                        confirm_btn.click()
                    
                    removed_count += 1
                    self.log(f"Removed follower {removed_count}/{self.limit}")
                    
                    # Speed Optimization: 1-3 seconds delay
                    # 1000 followers in 1 hour = ~3.6s per follower
                    # Operations take ~2s, so sleep 1-2s is ideal
                    sleep_time = random.uniform(1, 3)
                    self.log(f"Waiting {sleep_time:.1f}s...")
                    time.sleep(sleep_time)

                except Exception as e:
                    self.log(f"Error occurring: {e}")
                    time.sleep(2)
                    # Maybe scroll down if stuck
            
            self.log("Process Finished.")
            messagebox.showinfo("Done", f"Removed {removed_count} followers.")

        except Exception as e:
            self.log(f"Critical Error: {e}")
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.btn_stop.config(state=tk.DISABLED))

    def stop_removal(self):
        self.is_running = False
        self.log("Stopping...")

if __name__ == "__main__":
    root = tk.Tk()
    app = InstaRemoverApp(root)
    root.mainloop()
