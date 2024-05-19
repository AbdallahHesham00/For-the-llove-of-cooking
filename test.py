import unittest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import sqlite3
import os
import sys

current_directory = os.getcwd()
db_path = os.path.join(current_directory, "apps", "db.sqlite3")
image_path = os.path.join(current_directory, "Burger.PNG")

# Helper functions for cleaning up the database
def delete_test_user(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("DELETE FROM Users WHERE Username = 'test_user';")
    conn.commit()
    conn.close()

def delete_test_follows(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("DELETE FROM Followers WHERE FollowerId IN (SELECT Id FROM Users WHERE Username = 'followtester');")
    c.execute("DELETE FROM Followers WHERE FollowingId IN (SELECT Id FROM Users WHERE Username = 'followtester');")
    conn.commit()
    conn.close()

def delete_test_comment(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("DELETE FROM Comments WHERE UserId = 1 AND Content = 'Nice Meal';")
    conn.commit()
    conn.close()

def delete_test_rating(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("DELETE FROM Ratings WHERE UserId = 1;")
    conn.commit()
    conn.close()

def delete_recipe(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT Id FROM Recipes WHERE Title = 'Beef Burger';")
    result = c.fetchone()
    if result:
        recipe_id = result[0]
        c.execute("DELETE FROM Instructions WHERE RecipeId = ?", (recipe_id,))
        c.execute("DELETE FROM Ingredients WHERE RecipeId = ?", (recipe_id,))
        c.execute("DELETE FROM Ratings WHERE RecipeId = ?", (recipe_id,))
        c.execute("DELETE FROM Comments WHERE RecipeId = ?", (recipe_id,))
        c.execute("DELETE FROM Recipes WHERE Id = ?", (recipe_id,))
    conn.commit()
    conn.close()

class WebAppTests(unittest.TestCase):
    def setUp(self):
        if sys.platform.startswith('win'):
            self.driver = webdriver.Chrome(service=Service(os.path.join(current_directory, 'chromedriver_win32', 'chromedriver.exe')))
        else:
            self.driver = webdriver.Chrome(service=Service(os.path.join(current_directory, 'linux_chromedriver', 'chromedriver.exe')))
        self.driver.implicitly_wait(2)
    
    def tearDown(self):
        self.driver.quit()

    def test_login_success(self):
        driver = self.driver
        driver.get("http://localhost:5000")
        # Find the username and password input fields and enter the credentials
        username_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        username_field.send_keys("khalede@gmail.com")
        password_field.send_keys("Dodobasta5")

        # Submit the login form
        login_button = driver.find_element(By.NAME, "login")
        login_button.click()

        # Wait for the page to load after login (e.g., check for an element on the home page)
        driver.implicitly_wait(10)  # Wait for up to 10 seconds
        home_title = driver.find_element(By.XPATH, "//h1[contains(text(),'Welcome to Your Cookbook')]")
        assert home_title.is_displayed()

    def test_logout(self):
        driver = self.driver
        driver.maximize_window()
        driver.get("http://localhost:5000")
        # Find the username and password input fields and enter the credentials
        username_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        username_field.send_keys("khaled@gmail.com")
        password_field.send_keys("Dodobasta5")

        # Submit the login form
        login_button = driver.find_element(By.NAME, "login")
        login_button.click()

        # Wait for the page to load after login (e.g., check for an element on the home page)
        driver.implicitly_wait(10)  # Wait for up to 10 seconds
        # Find logout button and click it
        shut_down = driver.find_element(By.XPATH, '//*[@id="main-wrapper"]/aside/div[2]/div/div/a/i')
        shut_down.click()

        time.sleep(1)

        username_field = driver.find_element(By.NAME, "email")

        assert username_field.is_displayed()

    def test_registration_success(self):
        delete_test_user(db_path)
        driver = self.driver
        driver.get("http://localhost:5000")

        # Look for "register" button
        register_link = driver.find_element(By.LINK_TEXT, "Sign Up")
        register_link.click()

        # Fill user info
        username = driver.find_element(By.NAME, "username")
        username.send_keys("test_user")

        email = driver.find_element(By.NAME, "email")
        email.send_keys("test@example.com")

        password = driver.find_element(By.NAME, "password")
        password.send_keys("test_password")
        
        # Click register button
        register_button = driver.find_element(By.NAME, "register")
        register_button.click()

        # Wait for page to load
        time.sleep(2)
        # Check if registration is successful
        success_message = driver.find_element(By.XPATH, "//*[contains(text(), 'Sign-up successful')]")
        self.assertTrue(success_message.is_displayed())

    def test_registration_fail(self):
        driver = self.driver
        driver.get("http://localhost:5000")

        # Look for "register" button
        register_link = driver.find_element(By.LINK_TEXT, "Sign Up")
        register_link.click()

        # Fill user info
        username = driver.find_element(By.NAME, "username")
        username.send_keys("Khaled")

        email = driver.find_element(By.NAME, "email")
        email.send_keys("khaled@gmail.com")

        password = driver.find_element(By.NAME, "password")
        password.send_keys("Dodobasta5")

        # Click register button
        register_button = driver.find_element(By.NAME, "register")
        register_button.click()

        # Wait for page to load
        time.sleep(2)
        # Check if registration fails
        fail_msg = driver.find_element(By.XPATH, "//*[contains(text(), 'Email is already registered')]")
        self.assertTrue(fail_msg.is_displayed())
    
    def test_login_fail(self):
        driver = self.driver
        driver.get("http://localhost:5000")
        # Find the username and password input fields and enter invalid credentials
        username_field = driver.find_element(By.NAME, "email")
        password_field = driver.find_element(By.NAME, "password")
        username_field.send_keys("invalid_user@example.com")
        password_field.send_keys("invalid_password")

        # Submit the login form
        login_button = driver.find_element(By.NAME, "login")
        login_button.click()

        # Wait for the page to load after login attempt
        driver.implicitly_wait(10)  # Wait for up to 10 seconds
        error_message = driver.find_element(By.XPATH, "//*[contains(text(), 'Invalid email or password')]")
        self.assertTrue(error_message.is_displayed())

if __name__ == "__main__":
    unittest.main()
