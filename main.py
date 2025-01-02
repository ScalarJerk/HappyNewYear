from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from time import sleep
import pandas as pd
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whatsapp_automation.log'),
        logging.StreamHandler()
    ]
)

def setup_driver():
    """Initialize and configure Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def send_whatsapp_message(driver, phone_number, message, wait_time=35):
    """Send WhatsApp message to a single contact"""
    try:
        # Format phone number (remove any non-numeric characters)
        phone_number = str(phone_number).replace("+", "").replace("-", "").replace(" ", "")
        
        # Construct and load URL
        url = f'https://web.whatsapp.com/send?phone={phone_number}&text={message}'
        driver.get(url)
        
        # Wait for send button to be clickable
        send_button = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='send']"))
        )
        
        # Add a small delay before clicking
        sleep(2)
        send_button.click()
        sleep(3)  # Wait for message to be sent
        
        logging.info(f'Message sent successfully to {phone_number}')
        return True
        
    except TimeoutException:
        logging.error(f'Timeout while sending message to {phone_number}')
        return False
    except ElementClickInterceptedException:
        logging.error(f'Could not click send button for {phone_number}')
        return False
    except Exception as e:
        logging.error(f'Failed to send message to {phone_number}: {str(e)}')
        return False

def main():
    try:
        # Read CSV file
        try:
            csv_data = pd.read_csv('contacts.csv')
            if 'Phone 1 - Value' not in csv_data.columns:
                raise ValueError("Required column 'Phone 1 - Value' not found in CSV")
        except Exception as e:
            logging.error(f'Error reading CSV file: {str(e)}')
            return

        # Initialize driver
        driver = setup_driver()
        
        # Open WhatsApp Web
        driver.get('https://web.whatsapp.com')
        input("Press ENTER after logging into WhatsApp Web and your chats are visible...")
        
        # Track success/failure statistics
        successful_sends = 0
        failed_sends = 0
        
        # Send messages
        message = "Happy New Year! 🥳🎉🎊"
        for index, phone in enumerate(csv_data['Phone 1 - Value']):
            logging.info(f'Processing {index + 1}/{len(csv_data)}: {phone}')
            
            if send_whatsapp_message(driver, phone, message):
                successful_sends += 1
            else:
                failed_sends += 1
            
            # Add a delay between messages to avoid rate limiting
            sleep(3)
        
        # Log summary
        logging.info(f'\nSummary:\nSuccessful sends: {successful_sends}\nFailed sends: {failed_sends}')
        
    except Exception as e:
        logging.error(f'Script execution failed: {str(e)}')
    finally:
        if 'driver' in locals():
            driver.quit()
            logging.info("Browser closed successfully")

if __name__ == "__main__":
    main()