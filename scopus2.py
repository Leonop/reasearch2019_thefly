# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 15:08:51 2019

@author: 98089
"""

import pandas as pd
import requests,json,time
from selenium import webdriver
import os
from openpyxl.workbook import Workbook

if __name__ == '__main__':
    data_Ori = pd.read_excel('Link_file.xlsx')
    API_URL = 'https://api.elsevier.com/content/search/author?query=authlast({})%20and%20authfirst({})%20and%20affil({})&apiKey=8d63116fb74bb251c856f52e334b918a'
    header = {
            'Accept':'application/json'
            }
    schoolMap = [['FAMU', 'Florida Agriculture and Mechanical University'],
        ['FAU', 'Florida Atlantic University'],
        ['FGCU', 'Florida Gulf Coast University'],
        ['FIU', 'Florida International University'],
        ['FSU', 'Florida State University'],
        ['UCF', 'University of Central Florida'],
        ['UF', 'University of Florida'],
        ['UNF', 'University of North Florida'],
        ['USF', 'University of South Florida'],
        ['UWF', 'University of West Florida']]
    schoolMap = {i:j for i,j in schoolMap}

    browser = webdriver.Chrome('/Users/leono1/Sync/Research/ScopusAPI/driver/chromedriver')
    k = 1
    outcome = []
    for lastName,firstName,aff in data_Ori[['last_name','first_name','school']].values[510:618]:
        print('[%d]:'%k,end=' ')
        k += 1
        aff = schoolMap[aff]
        itemURL = API_URL.format(lastName, firstName, aff)
        res = requests.get(itemURL,headers=header)
        resJSON = json.loads(res.content)
        print(resJSON)
        try:
            #authorID = resJSON['search-results']['entry'][0]['dc:identifier'].split(':')[-1]
            num = len(resJSON['search-results']['entry'])
            for item in resJSON['search-results']['entry']:
                if item['affiliation-current']['affiliation-name'].lower() == aff.lower():
                    authorID = item['dc:identifier'].split(':')[-1]
                    break
            else:
                raise ValueError

        except Exception as e:
            print('Not Found This Author:%s %s(%s)'%(lastName,firstName,aff))
            continue
        print('%s %s(%s): %s'%(lastName,firstName,aff,authorID))

        authorURL = 'http://www.scopus.com/authid/detail.uri?authorId=%s'%authorID
        browser.get(authorURL)
        time.sleep(2)
        for tt in range(1,100):
            for articalDiv in browser.find_elements_by_xpath('//tr[starts-with(@id,"resultDataRow")]'):
                try:
                    articalName = articalDiv.find_element_by_xpath('./td[position()=1]/a').text
                    articalAuthors = articalDiv.find_element_by_xpath('./td[position()=2]').text
                    articalYear = articalDiv.find_element_by_xpath('./td[position()=3]/span').text
                    articalPub = articalDiv.find_element_by_xpath('./td[position()=4]').text
                    articalCite = articalDiv.find_element_by_xpath('./td[position()=5]').text
                    outcome.append([authorID,lastName,firstName,articalAuthors,
                            articalYear,articalName,articalPub,articalCite,aff,num])
                except Exception as e:
                    print(e)
                    continue
            pages = browser.find_elements_by_xpath('//ul[@class="pagination "]/li/a[@data-value]')
            for p in pages:
                if int(p.get_attribute('data-value')) == tt + 1:
                    p.click()
                    time.sleep(5)
                    break
            else:
                break

outcome = pd.DataFrame(outcome,columns=['AuthorID','Last Name','First Name','All Authors','Year','Title','Journal Name','Citation','Affiation','outcomeNum'])
path = '/Users/leono1/OneDrive/Research_2019/Jared_Project/'
outcome.to_csv(path+'outcome4.csv')
