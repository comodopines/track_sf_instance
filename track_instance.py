import requests
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import traceback

env_check_list = ["DEV", "STG", "PROD"]
instances = { "DEV" :
                    {
                      "domain" : "https://status.salesforce.com",
                      "uri_prefix" : "instances",
                      "instance_name" : "CSXX",
                      "uri_suffix" : "",
                      "overall_health_filter": "div.sc-iueMJG.gNlGiH",
                      "service_filter" : "div.sc-gGuQiZ.fAXLLe"
                    },
             "STG" :
                    {
                      "domain" : "https://status.salesforce.com",
                      "uri_prefix" : "instances",
                      "instance_name" : "CSXX",
                      "uri_suffix" : "",
                      "overall_health_filter": "div.sc-iueMJG.gNlGiH",
                      "service_filter" : "div.sc-gGuQiZ.fAXLLe"
                    },
             "PROD" :
                    {
                      "domain" : "https://status.salesforce.com",
                      "uri_prefix" : "instances",
                      "instance_name" : "NAXXX",
                      "uri_suffix" : "",
                      "overall_health_filter": "div.sc-iueMJG.gNlGiH",
                      "service_filter" : "div.sc-gGuQiZ.fAXLLe"
                    }

            }



def initialize_chrome():
    DRIVER_PATH='/Users/govindsinghrawat/python_scripts/ark/drivers/chromedriver'
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('headless')
    driver = webdriver.Chrome(options=chrome_options, executable_path=DRIVER_PATH)
    #https://stackoverflow.com/a/34838339/14885821
    
    return driver



def form_url(domain, instance_name, uri_prefix="", uri_suffix=""):
    protocol=""
    url_sep="/"
    url=""
    if "http://" not in domain and "https://" not in domain:
        protocol="https://"
    
    
    url=protocol+str(domain)

    if uri_prefix != "":
        url+=str(url_sep) + str(uri_prefix) + str(url_sep) + str(instance_name)
    
    if uri_suffix != "":
        url+=str(url_sep) + str(uri_suffix)

    return url


    
def get_chrome_driver(url):
    driver = initialize_chrome()
    driver.get(url)
    return driver


def get_overall_health(driver, tag="div.sc-iueMJG.gNlGiH", delimiter=","):
    div_table = driver.find_element_by_css_selector(tag)
    health_elements = div_table.find_elements_by_tag_name('span')
    row=""
    ok_health="HEALTHY"
    notok_health="UNHEALTHY"
    for span in health_elements:
        if row == "":
            row+=span.text
        elif span.text == "Available" and ok_health not in row:
            row+=delimiter+ok_health
        elif span.text != "Available" and ok_health not in row:
            row+=delimiter+notok_health

    return row

       
def get_services_health(driver, tag="div.sc-gGuQiZ.fAXLLe", delimiter=","):
    service_status=[]
    ok_health="HEALTHY"
    notok_health="UNHEALTHY"
    div_table = driver.find_elements_by_css_selector(tag)
    for div_elemi, div_element in enumerate(div_table):
        #print(str(div_elemi))
        div_elements = div_element.find_elements_by_tag_name('div')
        row=""
        for divsi, divs in enumerate(div_elements):
            div = divs.find_elements_by_tag_name('div')
            #print("|--> divs[",str(divsi),"]")
            #service=""
            #available=False
            if len(div) > 1:
                
                service=str(div[0].find_elements_by_tag_name('span')[0].text)
                
                status=div[1].find_elements_by_tag_name('span')[0].find_elements_by_css_selector("use")[0].get_attribute('xlink:href')

                if '#healthy' in status:
                    
                    row=service+str(delimiter)+ok_health
                elif '#unhealthy' in status:
                    
                    row=service+str(delimiter)+notok_health
                service_status.append(row)   
                
    return service_status


health_check = {}
delimiter=","
delay=10
for env in env_check_list:
    try:
        env_health = {}
        instance = instances[env]
        print(instance)
        env_url=form_url(str(instance["domain"]), str(instance["instance_name"]), str(instance["uri_prefix"]), str(instance["uri_suffix"]))
        print(env_url)
        oh_filter = str(instance["overall_health_filter"])
        print(oh_filter)
        driver = get_chrome_driver(env_url)
        try:
            wait = WebDriverWait(driver, delay)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, oh_filter)))
        except TimeoutException:
            print(env, ": Page Load Timeout")
            continue
        koverall,val = get_overall_health(driver,oh_filter,delimiter ).split(delimiter)
        env_health[koverall] = val
        
        print(oh_filter)
        #for sh_filter in instance["service_filter"]:
        #print(sh_filter)
        sh_filter=instance["service_filter"]
        service_health_dict={}
        for service_health in get_services_health(driver, sh_filter, delimiter):
            k,v = service_health.split(delimiter)
            service_health_dict[k] = v
        env_health["services"] = service_health_dict
        health_check[env] = env_health
            
                
    except KeyError:
        print("Missing Key")
        print(traceback.format_exc())
        sys.exit()
print(health_check)
