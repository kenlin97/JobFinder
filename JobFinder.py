from urllib.request import urlopen
import bs4
from bs4 import BeautifulSoup as soup
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from operator import itemgetter
import json


my_url = 'https://www.indeed.com/'

#CONFIGURATION VARIABLES
job_role = "Electrical Engineer"
location = "Pennsylvania"
pages_to_search = 4
keyword_list = ["electrical", "circuit", "pcb", "test", "entry", "python", "bachelor", "robot", "analog", "sensor", "fast", "firmware", "battery", "automation", "LTspice"
                , "robotics", "hardware"]
ignore_list = ["Principal", "staff", "manager", "senior", "Sr."]
filter_count = 3 #cutoff value for jobs that don't meet the number of keyword matches
output_filename = "jobs_PA.txt"

driver = webdriver.Chrome('C:/Users/mysti/PycharmProjects/Webscrape/drivers/chromedriver.exe')
#driver.maximize_window()
driver.set_page_load_timeout("10")
driver.get(my_url)

#time.sleep(2)
job_box = driver.find_element_by_name('q')
job_box.send_keys(job_role)
location_box = driver.find_element_by_name('l')
location_box.send_keys(Keys.CONTROL + "a")
location_box.send_keys(Keys.DELETE)
location_box.send_keys(location)
#time.sleep(2)
job_box.send_keys(Keys.ENTER)
#time.sleep(4)
print(driver.current_url)
jobdata_list = [] #contains a list of dictionaries of each job data
not_matched = 0
good_jobs = 0
error = False
for page in range(1, pages_to_search+1):
    window_before = driver.current_window_handle
    uClient = urlopen(driver.current_url) #uses url after the webdriver search
    html_page = uClient.read() #reads the page and converts to html
    uClient.close()
    soup_page = soup(html_page, "html.parser")
    jobs_list = soup_page.findAll("div", {"class": "jobsearch-SerpJobCard"})
    #print(len(jobs_list))

    #Clicks the job title to show description page for parsing more info
    click_list = driver.find_elements_by_class_name("jobtitle") #gets the list of element that can be clicked to show detailed job description
    print(str(len(click_list)) + " jobs found on page " + str(page))
    #clicklist[0].click() #clicks the element

    jobdata_dict = {}

    for index, job in enumerate(jobs_list):
        bad_job = False
        match_count = 0 #number of keyword matches in the job description
        if index < len(click_list): #makes sure that the number of jobs found doesn't exceed the number of clickable jobcards
            click_list[index].click() #clicks the job card
            driver.switch_to.window(driver.window_handles[1]) #switch working window to one newly opened
            #print(driver.current_url)
            job_link = driver.current_url
            try:
                uClient = urlopen(driver.current_url)
            except: #if error occurs when opening url, break from loop and stop the program.
                error = True
                break
            html_page_new = uClient.read()
            uClient.close()
            soup_page_new = soup(html_page_new, "html.parser")
            #parses job info from the new job page
            job_title = soup_page_new.find("div", {"class": "jobsearch-JobInfoHeader-title-container"}).text
            job_description = soup_page_new.find("div", {"class": "jobsearch-jobDescriptionText"}).text
            company_name = soup_page_new.find("div", {"class": "icl-u-lg-mr--sm"}).text
            driver.close()
            driver.switch_to.window(window_before) #switches back the working window to the original
            for keyword in keyword_list:
                if keyword.lower() in job_description.lower():
                    match_count +=1
            for word in ignore_list:
                if (word.lower() in job_description.lower()) or (word.lower() in job_title.lower()):
                    bad_job = True
            #store the data in the dictionary
            jobdata_dict["index"] = index
            jobdata_dict["title"] = job_title
            jobdata_dict["company"] = company_name.replace('\n', '')
            jobdata_dict["link"] = job_link
            jobdata_dict["similarity score"] = match_count

            jobdata_copy = jobdata_dict.copy()
            if (match_count > filter_count) and (bad_job == False):
                jobdata_list.append(jobdata_copy) #adds the dictionary to the list
                good_jobs += 1
            else:
                not_matched += 1
    if error:
        print("Error occurred")
        break
    print("page " + str(page) + " checked!")
    time.sleep(1)
    #clicks to next page
    while True:
        try:
            driver.find_element_by_css_selector("[aria-label='Next']").click()
            break
        except NoSuchElementException:
            print("No more pages to search")
            break
    #print(driver.find_element_by_css_selector("[aria-label='Close']"))
    time.sleep(1)

    #driver.find_element_by_xpath("//body").click()
    actions = ActionChains(driver)
    actions.send_keys(Keys.ESCAPE).perform()
    #driver.find_elements_by_class_name("icl-CloseButton popover-x-button-close").click()

print("Filtered out jobs: " + str(not_matched))
print("Passed match criteria: " + str(good_jobs))

sorted_joblist = sorted(jobdata_list, key=itemgetter('similarity score'), reverse= True) #sorts the job list based on similary score, shows the highest score at the top

#dumps to text file
output_file = open(output_filename, "w", encoding='utf-8')
for jobdict in sorted_joblist:
    json.dump(jobdict, output_file)
    output_file.write("\n")

driver.quit()









