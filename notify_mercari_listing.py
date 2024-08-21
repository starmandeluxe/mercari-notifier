import unittest
import time
import sys
import locale
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException 
import smtplib
from email.mime.text import MIMEText
import chromedriver_autoinstaller
from pyvirtualdisplay import Display

display = Display(visible=0, size=(800, 800))  
display.start()

import _locale
_locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])


def main():
	"""Find out if there's a desired listing posted on Mercari, and notifies user if there was."""
	sys.stdout.reconfigure(encoding='utf-8')

	# Get email addresses.
	from_email = os.environ['FROM_EMAIL']
	to_email = os.environ['TO_EMAIL']

	# Retrieve the secret to login to Gmail.
	gm = os.environ['GM']

	# Set the keyword and sub-keywords that we are looking for of what we want to purchase.
	query_string = os.environ['MERCARI_KEYWORD_QUERY_STRING']
	needle = os.environ['SUB_KEYWORD_SEARCH']

	# Setup Selenium.
	chromedriver_autoinstaller.install()
	chrome_options = Options()
	options = [
		"--headless",
		"--disable-gpu",
		"--window-size=1920,1200",
		"--ignore-certificate-errors",
		"--disable-extensions",
		"--no-sandbox",
		"--disable-dev-shm-usage"
	]

	for option in options:
		chrome_options.add_argument(option)

	chrome_options.add_experimental_option("detach", True)

	browser = webdriver.Chrome(options=chrome_options)

	# Make the GET request to perform the product listing search.
	browser.get(f'https://jp.mercari.com/search?keyword={query_string}')
	browser.implicitly_wait(10)

	# Scroll down in order to get the entire page.
	try:
		html = browser.find_element(By.XPATH,'//body')
		scrolled_amount = 0
		page_height = browser.execute_script("return document.body.scrollHeight")
		print(f'HEIGHT: {page_height}')
	except NoSuchElementException as exception:
		print('Could not find element', exception)
	except TimeoutException as exception:
	    print('Loading took too much time!')
	
	while scrolled_amount < page_height:
		try:
			html.send_keys(Keys.PAGE_DOWN)
			scrolled_amount += 100
			time.sleep(.5)
		except StaleElementReferenceException as exception:
			print('Element became stale while scrolling down')
			html = browser.find_element(By.XPATH,'//body')
			continue

	# Find all the titles of the search result listings.
	try:
		li_list = browser.find_elements(By.XPATH, "//li[starts-with(@class,'sc-bcd1c877-2 cvAXgx')] //descendant::div //descendant::a //descendant::div[starts-with(@class,'merItemThumbnail')]")
		print(f'NUMBER OF RESULTS ON PAGE: {len(li_list)}')

		results = ''

		for i in range(0, len(li_list)):
			sub_element = browser.find_elements(By.XPATH, "//li[starts-with(@class,'sc-bcd1c877-2 cvAXgx')] //descendant::div //descendant::a //descendant::div[starts-with(@class,'merItemThumbnail')]")[i]
			haystack = sub_element.get_attribute("aria-label")
			if haystack:
				print(f'Successfully found {i+1} search results')

				# Filter for a specific string of what we are looking for.
				if needle in haystack:
					print(f'HIT FOUND INSIDE SEARCH RESULT #{i}: {haystack}')
					link_element = sub_element.find_element(By.XPATH, '..')
					link = link_element.get_attribute('href')

					# If a match was found, save its hyperlink to be emailed later.
					print(f'LINK TO THE HIT: {link}')
					results += link + '\n'

		# Only if a match was found, email all the results to myself.
		if results:
			print(f'SUCCESSFUL FIND! FINAL RESULTS TO EMAIL: {results}')
			_send_email(results, from_email, to_email, gm)
		else:
			print("NO MATCH IN THE SEARCH HITS WAS FOUND THIS TIME AROUND. TRY AGAIN NEXT TIME!")
	except NoSuchElementException as exception:
		print('Could not find element', exception)
	except TimeoutException as exception:
	    print('Loading took too much time!')
	finally:
		browser.quit()

def _send_email(contents, sender, recipient, password) -> None:
	"""Sends an email.
		
		Args:
			contents: contents of the email body.
			sender: sender email address.
			recipient: receiver email address.
			password: email password.

		Returns: 
			None
	"""
	msg = MIMEText(contents)
	msg['From'] = sender
	msg['To'] = recipient
	msg['Subject'] = "Congrats, someone just listed a Soundcore LEFT earbud for sale!"

	with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
		smtp_server.login(sender, password)
		smtp_server.sendmail(sender, [recipient], msg.as_string())

	print(f'EMAIL SENT TO {recipient}')

if __name__ == "__main__":
	main()