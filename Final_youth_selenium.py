#!/usr/bin/env python
# coding: utf-8

# In[3]:


import selenium
from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import pandas as pd
import re
import sqlite3


# In[4]:


df_code = pd.read_csv('final_code.csv').drop('Unnamed: 0', axis = 1)
final_AREA = pd.read_csv('./final_area_df.csv').drop('Unnamed: 0', axis = 1)
overlap_check = pd.read_csv('./overlap_check.csv').drop('Unnamed: 0', axis = 1)
host_check = ['동구', '북구', '서구', '남구', '강서', '중구', '고성']


# In[10]:


def youth():
    
    # 크롬 드라이버 저장된 위치
    cromedriver_path = 'D:\chromedriver'
    
    URL = 'https://www.youthcenter.go.kr/youngPlcyUnif/youngPlcyUnifList.do?pageIndex=1&pageUnit=60'
    driver = webdriver.Chrome(executable_path=cromedriver_path)
    driver.get(url=URL)

    last_page = driver.find_element_by_class_name('paging')
    last_page_btn = last_page.find_element_by_class_name('btn_last')
    last_page_btn.click()

    last_page = driver.find_element_by_class_name('paging')
    last_page_num = last_page.find_element_by_class_name('active').text
    page_num = int(last_page_num)


    DF_youth = pd.DataFrame(columns = ['title', 'href', 'age_min', 'age_max', 'area', 'work', 'type', 'host'])
    driver.close()


    for page in range(1, page_num+1):
        driver = webdriver.Chrome(executable_path=cromedriver_path)
        URL = 'https://www.youthcenter.go.kr/youngPlcyUnif/youngPlcyUnifList.do?pageIndex=' + str(page) + '&pageUnit=60'
        driver.get(url=URL)

        num = driver.find_element_by_class_name('result-list-box').find_elements_by_tag_name('li')
               
        for index in range(1, len(num)+1):
            
            try:
                type_xpath = '//*[@id="srchFrm"]/div[4]/div[2]/ul/li[' + str(index) + ']/div[2]/span'
                type_str = driver.find_element_by_xpath(type_xpath)
                type_str = type_str.get_attribute('innerHTML').replace('\t', "").replace('\n', "").replace('<span>', " ").replace('</span>', "")
            except:
                type_str = '기타'
                        
            xpath = '//*[@id="srchFrm"]/div[4]/div[2]/ul/li[' + str(index) + ']/a'
            e = driver.find_element_by_xpath(xpath)
            e.send_keys(Keys.ENTER)

            title = driver.find_element_by_class_name('plcy-left')
            title = title.text

            href = driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[2]/div[3]/ul/li[3]/div[2]/a')
            if href.text == "" or href.text == "-":
                href = driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[2]/div[4]/ul/li[4]/div[2]/a')
            href = href.text

            host_xpath = '//*[@id="content"]/div[1]/div[2]/div[4]/ul/li[2]/div[2]'
            host = driver.find_element_by_xpath(host_xpath).text
            
            ul = driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[2]/div[2]/ul')
            list_cont = ul.find_elements_by_class_name('list_cont')

            age = list_cont[0].text
            area = list_cont[1].text
            work = list_cont[2].text

            age = re.findall('\d+', age)
            if len(age) == 2:
                age_min = int(age[0])
                age_max = int(age[1])
            elif len(age) == 1:
                age_min = 0
                age_max = int(age[0])
            else:
                age_min = 0
                age_max = 999


            DF_youth.loc[len(DF_youth.index)] =  {'title' : title, 'href' : href, 'age_min' : age_min, 'age_max' : age_max, 'area' : area, 'work' : work, 'type' : type_str, 'host' : host }

            URL = 'https://www.youthcenter.go.kr/youngPlcyUnif/youngPlcyUnifList.do?pageIndex=' + str(page) + '&pageUnit=60'
            driver.get(url=URL)
            

        driver.close()
    
    
    
    
    # area 처리    
    youth_area_code = []
    youth_area_list = []

    for i in range(len(DF_youth.index)):
        area_text = DF_youth['area'][i]
        code = len(df_code.index)
        area_list = ""

        # 시도 이름 있는지 확인
        for index in range(len(df_code)):
            find_index = area_text.find(df_code['SiDo'][index])
            if find_index >= 0:
                try:
                    if index == 5 and area_text[find_index:find_index+4] == "대구성원":
                        continue
                    else:
                        code = index
                except IndexError:
                    code = index
                break


        # 이름 같은 시군구 확인
        for index in range(len(host_check)):
            find_index = area_text.find(host_check[index])

            if find_index >= 0:            
                is_overlap = 0
                # '강서구 --> 서구' 와 같은 경우는 pass
                for overlap_index in range(len(overlap_check.index)):
                    if host_check[index] == overlap_check['overlap'][overlap_index]:
                        if area_text[find_index-1:find_index+len(host_check[index])].find(overlap_check['notOverlap'][overlap_index]) >= 0:
                            is_overlap = 1


                # 이름이 같은 시군구에 해당하고 시도code 미정인 경우 host 확인
                if is_overlap == 0:
                    if len(area_list) == 0:
                        area_list += host_check[index]
                    elif area_list.find(host_check[index]) < 0:
                        area_list += (', ' + host_check[index])

                    if code >= len(df_code.index):
                        host = DF_youth['host'][i]
                        for code_index in range(len(df_code.index)):
                            if host.find(df_code['SiDo'][code_index]) >= 0:
                                code = code_index
                                break



        # 나머지 시군구 확인
        for index in range(len(final_AREA.index)):
            find_index = area_text.find(final_AREA['GunGu_search'][index])
            if find_index >= 0:

                #예외 상황1 (자주 확인해서 추가해야 함)
                if find_index > 0:
                    ## 남양주 --> 양주
                    if final_AREA['GunGu_search'][index] == "양주" and area_text[find_index-1] == "남":
                        continue
                                ## 급여수급자 --> 여수
                    elif final_AREA['GunGu_search'][index] == "여수" and area_text[find_index-1] == "급":
                        continue

                    ## 종사하는 --> 사하
                    elif final_AREA['GunGu_search'][index] == "사하" and area_text[find_index-1] == "종":
                        continue

                    ## 공공주택 --> 공주
                    elif final_AREA['GunGu_search'][index] == "공주" and area_text[find_index-1] == "공":
                        continue                

                    ## 신청주의 --> 청주
                    elif final_AREA['GunGu_search'][index] == "청주" and area_text[find_index-1] == "신":
                        continue                    

                    ## 경영주 --> 영주
                    elif final_AREA['GunGu_search'][index] == "영주" and area_text[find_index-1] == "경":
                        continue     

                #예외 상황2    
                if find_index+2 < len(area_text):
                    ## 무주택 --> 무주
                    if final_AREA['GunGu_search'][index] == "무주" and area_text[find_index+2] == "택":
                        continue

                    ## 고령자 --> 고령
                    elif final_AREA['GunGu_search'][index] == "고령" and area_text[find_index+2] == "자":
                        continue

                        continue

                    ## 부산청년 --> 산청
                    elif final_AREA['GunGu_search'][index] == "산청" and area_text[find_index+2] == "년":
                        continue



                ## only 부여군 --> 부여
                if final_AREA['GunGu_search'][index] == "부여" and area_text[find_index+2] != "군":
                    continue




                # 이미 코드가 있는 경우는 pass
                if code >= len(df_code.index):
                    code = final_AREA['SiDo_search'][index]

                # dlfms wjwkd
                if len(area_list) == 0:
                    area_list += final_AREA['GunGu_search'][index]
                elif area_list.find(final_AREA['GunGu_search'][index]) < 0:
                    area_list += (', ' + final_AREA['GunGu_search'][index])


        youth_area_code.append(code)
        youth_area_list.append(area_list)
    

    DF_youth['area_code'] = youth_area_code
    DF_youth['area_list'] = youth_area_list
    
    final_df = DF_youth[['title', 'age_min', 'age_max', 'area_code', 'area_list', 'work', 'type', 'area', 'host', 'href']]
    
    
    conn = sqlite3.connect('database.db')
    final_df.to_sql('youth', conn, if_exists='replace')
    


# In[11]:


youth()

