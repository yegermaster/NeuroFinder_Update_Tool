from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import old_code.constants as c

driver = webdriver.Chrome()

driver.get("https://finder.startupnationcentral.org/")

try:
    # Attempt to click a generic login button; adjust the selector as needed.
    login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='login-button'], .login, button[name='login']"))
    )
    login_button.click()
except Exception as e:
    print("Error finding the login button:", e)
    driver.quit()  # Quit the driver if the login button cannot be found

try:
    username_field = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input_username_selector"))
    )
    password_field = driver.find_element(By.CSS_SELECTOR, "input_password_selector")

    username_field.send_keys(c.USERNAME)
    password_field.send_keys(c.PASSWORD)

    # Assuming there's a submit button for the form, replace 'submit_button_selector' with the actual selector
    login_submit_button = driver.find_element(By.CSS_SELECTOR, "submit_button_selector")
    login_submit_button.click()
except Exception as e:
    print("Error in login form interaction:", e)

# Add your navigation and interaction code here

driver.quit()
