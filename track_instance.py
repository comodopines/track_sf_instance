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
                #print("++++++++++++++++",div[0].find_elements_by_tag_name('span')[0].text)
                service=str(div[0].find_elements_by_tag_name('span')[0].text)
                #print("++++++++++++++++",div[1].find_elements_by_tag_name('span')[0].find_elements_by_css_selector("use")[0].get_attribute('xlink:href'))
                status=div[1].find_elements_by_tag_name('span')[0].find_elements_by_css_selector("use")[0].get_attribute('xlink:href')

                if '#healthy' in status:
                    #print(service, "healthy")
                    row=service+str(delimiter)+ok_health
                elif '#unhealthy' in status:
                    #print(service, "unhealthy")
                    row=service+str(delimiter)+notok_health
                service_status.append(row)   
                #available=False
                #for di, d in enumerate(div):
                #    print("|  |--> di[",str(di),"]")
                #    spans= d.find_elements_by_tag_name('span')
                #    for si, s in enumerate(spans):
                #        print("|  |  |--> si[",str(si),"]", str(s.text))
                #        #print("divsi[", str(divsi)+"], di[",str(di),"], si[",str(si),"] span_s.text ----->", s.text)
                #        hrefs = s.find_elements_by_css_selector("use")
                #        #print("   |---->", str(s.tag_name), str(s.text) , str(hrefs.get_attribute('href')), str(hrefs.get_property('href')), str(hrefs.get_attribute('xlink:href')), str(hrefs.get_property('xlink:href')))
                #        for hi, h in enumerate(hrefs):
                #            if di == 0 and si == 0:
                #                #print("|  |  |  |--> h[",str(hi),"]", s.text)
                #                service=s.text
                #                #print("h : --->", type(h), str(h.tag_name),str(h.get_attribute('href')), str(h.get_property('href')), str(h.get_attribute('xlink:href')), str(h.get_property('xlink:href')) )
                #                #print("divsi[", str(divsi)+"], di[",str(di),"], si[",str(si),"], hi[",str(hi),"]  h href |----->", str(h.get_attribute('xlink:href')))
                #            elif di ==1 and si == 0:
                #                #print("|  |  |  |--> h[",str(hi),"]", s.text,str(h.get_attribute('xlink:href')))
                #                if "#healthy" in str(h.get_attribute('xlink:href')):
                #                    available=True
                #                else:
                #                    available=False
                #                break
                #print(service,available)               
        
                #print("~~~~~~~~~~~~~~~~~")
                #print("|")

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
