import bs4
import os
import time
import mysql.connector

from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

#Connect to mysql server database using your login
db = mysql.connector.connect(
   user = "----",
   password = "----",
 host= "localhost",
   database = "tacomacarfaxlist"
)

mycursor = db.cursor()
mycursor.execute("CREATE TABLE TacomaList (Model VARCHAR(1000), Price INT(100), Mileage INT(100), Title VARCHAR(1000), Location VARCHAR(1000), Color VARCHAR(50), Drivetrain VARCHAR(20), Bodystyle VARCHAR(20), Cab VARCHAR(20), Engine VARCHAR(30)) ")

#Connects to google chrome disk driver and opens up given url, waits 3 seconds for page to load
driver = webdriver.Chrome()
driver.get("https://www.carfax.com/Used-Toyota-Tacoma_w641")
time.sleep(3)

#Enters given data into specified data fields and clicks on listed elements. Once actions are complete, wait for
#3 seconds
def page_nav():
   enter_zip = driver.find_element_by_xpath('//*[@id="make-model"]/form/div[3]/div/div[4]/div/input')
   enter_zip.send_keys('85248')
   enter_radius = driver.find_element_by_xpath('//*[@id="radius_3000"]')
   enter_radius.click()
   search_results = WebDriverWait(driver, 1).until(
       EC.visibility_of_element_located((By.XPATH, "//*[@id=\"make-model-form-submit\"]")))
   driver.execute_script("arguments[0].click();", search_results)
   time.sleep(3)


#Main function that reads elements of each page and assigns these elements to local variables and sends the data to a
#mysql table
def main_run():
   counting = 0
   condition = True
   #Each time a new page is opened we want to refresh the page source and examine the new containers
   while condition is True:
       time.sleep(3)
       html = driver.page_source
       page_soup = soup(html, "html.parser")
       containers = page_soup.findAll("div", {"class": "srp-list-container"})

      #Loops through and locates each individual elements(container) within the containers
       for container in containers:

           #Assigning elements within the container to local variables
           listing_type = container.findAll("div", {"class": "listing-header"})
           listing_price = container.findAll("span", {"class": "srp-list-item-price"})
           title_status = container.findAll("span", {"class": "title"})
           location_sold = container.findAll("div", {"class": "srp-list-item-dealership-location"})
           basic_info = container.findAll("div", {"class": "srp-list-item-basic-info srp-list-item-special-features"})
           basic_info_two = container.findAll("span", {"class": "srp-list-item-basic-info-value"})
           car_description = container.findAll("span", {"class": "srp-list-item-options-descriptions"})

           #Iterating counters used in program
           i = 0
           j = 0
           z = 0
           t = 0
           a = 0

           #Loops through the elements within the container, applies conditional formatting to determine what values
           #will be stored and sent to the mysql database table
           while i < len(listing_type):
               listing_name = listing_type[i].text
               price = listing_price[i].text
               if price is None:
                   price = int("0")

               else:
                   price = price.replace("Price:", "")
                   price = price.replace("$", "")
                   price = price.replace(",", "")
                   price = int(price)

               location = location_sold[i].text
               if location is None:
                   location = "None"

               else:
                   location = location.replace("Location:", "")

               description = car_description[i].text.split(',')

               while t < len(basic_info[i]):
                   if "Mileage" in basic_info[i].text:
                       mileage = basic_info_two[z + t].text
                       mileage = mileage.replace("Mileage:", "")
                       mileage = mileage.replace(",", "")
                       mileage = mileage.replace("miles", "")
                       mileage = int(mileage)
                       t += 1
                   else:
                       mileage = int("0")

                   if "Body Type" in basic_info[i].text:
                       body_style = basic_info_two[z + t].text
                       body_style = body_style.replace("Body Type:", "")
                       t += 1
                   else:
                       body_style = "None"

                   if "Color" in basic_info[i].text:
                       color = basic_info_two[z + t].text
                       color = color.replace("Color:", "")
                       t += 1
                   else:
                       color = "None"

                   if "Engine" in basic_info[i].text:
                       engine = basic_info_two[z + t].text
                       engine = engine.replace("Engine:", "")
                       t += 1
                   else:
                       engine = "None"

                   z += len(basic_info[i])

               if i == 0:
                   title = title_status[i].text

               else:
                   j += 4
                   title = title_status[j].text

               if description is None:
                   drive = "None"
                   cab = "None"

               else:
                   while a < len(description):
                       if "4WD" in description[a]:
                           drive = "4WD"
                       if "RWD" in description[a]:
                           drive = "RWD"
                       if "Double Cab" in description[a]:
                           cab = "Double Cab"
                       if "Access Cab" in description[a]:
                           cab = "Access Cab"
                       a += 1

               #Prints the results for the current container
               print(listing_name + " ", price, " ", mileage, " " + title + " " + location + " " + color)
               print(drive + " " + body_style + " " + cab + " " + engine)

               #Inserts the results into a mysql table
               sql_formula = ("INSERT INTO TacomaList (Model, Price, Mileage, Title, Location, Color, Drivetrain, Bodystyle, Cab, Engine)" "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
               mycursor.execute(sql_formula, (listing_name, price, mileage, title, location, color, drive, body_style, cab, engine))
               db.commit()

               i += 1
               t = 0
               a = 0

       #If the button to the next page exists, than it is select, else the method is terminated

       next_page = driver.find_element_by_xpath('//*[@id="ucl-microapp-srp-content"]/div/div[3]/div[2]/div/ul/button[2]')
       next_page.click()
       counting += 1

       if counting == 51:
           print("End of List")
           break

       print(counting)
       print("--------------------------------------------")
   db.close()

#Running Functions
page_nav()
main_run()
