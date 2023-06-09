from os import pipe
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
import time
import requests
from lxml import etree
#encoding: utf-8
def create_ip_pool():
    headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    }
    fp = open("ipPool.txt",'w',encoding= 'utf-8')
    print("==========================正在构造IP池===================================")
    for i in range(1,2001):
        url = 'http://www.xiladaili.com/gaoni/'+str(i)+'/'
        respones = requests.get(url=url,headers=headers).text
        tree = etree.HTML(respones)
        tree_list_gao_ni = tree.xpath('//tbody/tr/td[1]/text()')
        for i in range(0,len(tree_list_gao_ni)):
            proxy = tree_list_gao_ni[i]	
            proxies = {
	        'http': 'http://' + proxy
		    }
            print('==========================检测IP是否可用===================================')
            try:
                is_valid = requests.get('https://www.baidu.com/',headers=headers,proxies=proxies)
                if len(is_valid.content) > 100:
                    print('当前代理可用:'+tree_list_gao_ni[i])
                    fp.write(tree_list_gao_ni[i]+'\n')
            except Exception:
                print('不可用ip代理'+tree_list_gao_ni[i])
            finally:
                print('当前代理'+tree_list_gao_ni[i]+'检测完毕')
    fp.close()   
    print('==========================IP池构造完毕===================================') 
def init():
    # 使用selenium
    #opt = webdriver.ChromeOptions()
    #opt .add_argument("–proxy-server=http://186.29.163.97:49787")# 一定要注意，等号两边不能有空格
    web = webdriver.Chrome()
    web.get('https://tieba.baidu.com/f?ie=utf-8&kw=%E6%89%8B%E6%9C%BA&fr=search')
    #time.sleep(30)
    return web
def get_all_link(web):
    # 获取帖子总数
    n = web.find_elements_by_xpath('//*[@id="pagelet_frs-list/pagelet/thread_list"]/div/div[2]/div/span')[0]
    number = int(n.text)
    print(number)
    # 执行获取每个帖子链接
    counts = 0
    for m in range(17000,number,50):
        counts += 1
        if(counts % 10 == 0):
            print('Have a rest')
            time.sleep(10)
        li_list = web.find_elements_by_xpath('//div[@id="pagelet_frs-list/pagelet/thread_list"]//li[@class=" j_thread_list clearfix thread_item_box"]')
        # 处理本页的每一个帖子
        count = 1
        for i in li_list:
            try:
                # 如果用户不是vip
                s = i.find_element_by_xpath('./div[@class="t_con cleafix"]//div[@class="threadlist_title pull_left j_th_tit "]/a')
            except:
                try:
                # 如果用户是vip
                    s = i.find_element_by_xpath('./div[@class="t_con cleafix"]//div[@class="threadlist_title pull_left j_th_tit  member_thread_title_frs "]/a')
                except:
                    continue
            
            # 获取帖子地址以及标题
            url   = s.get_attribute("href")
            info  = s.text
            # 输出信息
            print(url+ ":"+info)
            #对每一个帖子进行处理
            #跳转目标页面
            
            try:
                s.click()
                web.switch_to.window(web.window_handles[-1])
                every_info(web,info)
                web.close()
                web.switch_to.window(web.window_handles[0])
                if count == len(li_list):
                    break
            except:
                continue
            print(len(li_list))
            print(count)
            count += 1
        next = "https://tieba.baidu.com/f?kw=%E6%89%8B%E6%9C%BA&ie=utf-8&pn="+str(m)
        print("=========================================================================================================")
        web.get(next)
        print(web.current_url)
def every_info(web,info): 
     next_url_save = web.current_url     
     s = web.find_element_by_xpath('//body').get_attribute("class")
     if s == 'page404':
         return
     # 首先确定每个帖子的页数
     n = web.find_elements_by_xpath('//li[@class="l_reply_num"]/span')[3]
     num = int(n.text)
     # 提取贴吧主题
     tie_themem =  web.find_elements_by_xpath('//*[@id="j_core_title_wrap"]/div[2]/h1')[0].text
     print(tie_themem)
     # 对帖子所有页进行信息提取
     try:
         m = open(info,'r')
         return
     except:
         fp = open(info,'w',encoding='utf-8')
     for page in range(1,num):
        lists = web.find_elements_by_xpath('//div[@id="j_p_postlist"]/div')
        js = "window.scrollBy(0,1000)"
        for i in range(0,len(lists)):
            if i > 0 :
                fp = open(info,'a',encoding='utf-8')
        # 主回复
            web.execute_script(js)
            tie__name = lists[i].find_element_by_xpath('.//li[@class="d_name"]/a').text
            if tie__name == "百度AI市场":
                continue
            '''
            <ul class="p_tail"><li><span>1楼</span></li><li><span>2021-09-21 13:39</span></li></ul>
            '''
            try:
                tie__time = lists[i].find_element_by_xpath('.//ul[@class="p_tail"]/li[2]/span').text
                #print("回复时间是"+tie__time)
                tie__floor = lists[i].find_element_by_xpath('.//ul[@class="p_tail"]/li[1]/span').text
                #print("回复楼层是"+tie__floor)
                tie__content = lists[i].find_element_by_xpath(
                    './/div[@class="d_post_content j_d_post_content  clearfix"]').text
                print(tie__time[0:-1]+tie__floor+tie__name+':'+tie__content)
                fp.write(tie__time)
                fp.write('-')
                fp.write(tie__floor)
                fp.write('-')
                fp.write(tie__name)
                fp.write(':')
                fp.write(tie__content)
                fp.write('\n')
            except:
                web.execute_script("window.scrollBy(0,300)")            
         # 继续爬取下一页帖子信息
        fp.close()
        next_url =  next_url_save + '?pn='+str(page)
        web.get('https://tieba.baidu.com/')
        web.get(next_url)
        time.sleep(1)
     return 
         
def scroll_foot(self):
    '''
    滚动条拉到底部
　　:return:
　　'''
    js = "var q=document.documentElement.scrollTop=300"
    #将滚动条移动到页面的顶部
    # js="var q=document.documentElement.scrollTop=0"
    return self.driver.execute_script(js)
def changeIP(web,fp_ip):
        time.sleep(2)
        current_url =  web.current_url
        opt = webdriver.ChromeOptions()
        opt .add_argument("–proxy-server=http://"+fp_ip.readline())# 一定要注意，等号两边不能有空格
        web = webdriver.Chrome(options=opt)
        web.get(current_url) 
if __name__ == '__main__':
    # 构造ip池
    #create_ip_pool()
    get_all_link(init())



#web.set_proxy(web, http_addr="212.35.56.22", http_port=8888)
