# -*- coding: UTF-8 -*-
from time import sleep  # 浏览器载入时间
from selenium import webdriver  # Web浏览器模块
from bs4 import BeautifulSoup  # BeautifulSoup模块
from selenium.webdriver.common.keys import Keys  # 键盘按键动作
from selenium.webdriver.support.wait import WebDriverWait  # 浏览器等待
import re
import xlwt
import selenium


'''
知乎用户爬虫
Author:Hayaohiko(admin@ruchope.org)
Last submit:170925_1
'''


def init_work():
    """
    初始化浏览器
    :return:Selenium浏览器对象
    """
    browser = webdriver.Chrome(executable_path='./driver/chromedriver')
    return browser


def handle_login(zh_username, zh_pwd, p_url):
    """
    实现知乎登陆,并返回首页内容
    :param zh_username:知乎用户名
    :param zh_pwd:知乎密码
    :param p_url:起始链接
    :return:知乎首页的HTML文本
    """
    driver.set_window_size(960, 540)
    driver.get(p_url)
    sleep(2)
    driver.find_element_by_xpath("//*[@class='signin-switch-password']").click()
    elem = driver.find_element_by_xpath("//*[@name='account']")
    elem.send_keys(zh_username)
    elem = driver.find_element_by_xpath("//*[@name='password']")
    elem.send_keys(zh_pwd)
    elem.send_keys(Keys.ENTER)
    wait = WebDriverWait(driver, 15)
    p_page_source = driver.page_source
    return p_page_source


def download_page_html(p_url):
    """
    下载指定页面的HTML文本
    :param p_url: 链接
    :return: HTML文本
    """
    driver.get(p_url)
    sleep(2)
    p_page_source = driver.page_source
    return p_page_source


def init_bs_object(p_page_source):
    """
    将HTML文本转换为BS对象
    :param p_page_source:HTML文本
    :return:BS对象
    """
    try:
        bs_object = BeautifulSoup(p_page_source, 'lxml')
    except AttributeError as e:
        print(e)
        return None
    return bs_object


def complete_url_link(p_url):
    """
    将采集到的链接补全
    !!!WARNING!!!仅限域名WWW.ZHIHU.COM内容
    :param p_url:待补全链接
    :return:补全后链接
    """
    if p_url is None:
        return None
    else:
        if p_url.startswith('//'):
            return 'https:' + p_url
        elif p_url.startswith('/'):
            return 'https://www.zhihu.com' + p_url
        elif p_url.startswith('http'):
            return p_url
        else:
            return None


def init_href_list(p_bs_object):
    """
    将BS对象的所有超链接补全输出(包括内链和外链)
    :param p_bs_object:BS对象
    :return:BS对象所有超链接的列表
    """
    a_elem_list = p_bs_object.findAll("a")
    p_href_list = []
    for i_item in a_elem_list:
        a_full_url = complete_url_link(i_item.get('href'))
        if a_full_url is None:
            continue
        else:
            p_href_list.append(a_full_url)
    return p_href_list


class ZhUser:
    def __init__(self, user_id):
        self.is_null = False
        self.user_id = user_id
        activities_url = "https://www.zhihu.com/people/" + self.user_id + "/following"
        driver.get(activities_url)
        sleep(2)
        try:
            driver.find_element_by_xpath("//*[@class='ProfileHeader-title']")
        except selenium.common.exceptions.NoSuchElementException as e:
            self.is_null = True
        try:
            driver.find_element_by_xpath("//*[@class='Button ProfileHeader-expandButton Button--plain']").click()
        except selenium.common.exceptions.NoSuchElementException as e:
            pass
        if self.is_null is False:
            activities_page = driver.page_source
            act_bs_object = init_bs_object(activities_page)
            self.user_name = act_bs_object.find("span", class_="ProfileHeader-name").get_text()
            try:
                live_str_list = act_bs_object.find("span", text="居住地").next_sibling.children
                self.live_now = self.get_live_content(live_str_list)
            except AttributeError as e:
                self.live_now = "NULL"
            try:
                self.job = act_bs_object.find("span", text="所在行业").next_sibling.get_text()
            except AttributeError as e:
                self.job = "NULL"
            try:
                self.answers = act_bs_object.find("a", href="/people/%s/answers"%self.user_id).span.get_text()
                self.asks = act_bs_object.find("a", href="/people/%s/asks" % self.user_id).span.get_text()
                self.posts = act_bs_object.find("a", href="/people/%s/posts" % self.user_id).span.get_text()
                self.pins = act_bs_object.find("a", href="/people/%s/pins" % self.user_id).span.get_text()
                self.follow_to = act_bs_object.find("div", text="关注了").next_sibling.get_text()
                self.follow_by = act_bs_object.find("div", text="关注者").next_sibling.get_text()
            except AttributeError as e:
                self.is_null = True
            try:
                agrees_string = act_bs_object.find("div", class_="IconGraf").get_text()
                self.agrees = re.sub("\D", "", agrees_string)
            except AttributeError as e:
                self.agrees = "0"
            # Hayaohiko(admin@ruchope.org):(待修改)以下TRY分支不正确,应当判断文本内容而不是简单的出错便判定不存在.
            try:
                thanks_str = act_bs_object.find("div", class_="Profile-sideColumnItemValue").get_text()
                self.thanks = re.sub("\D", "", thanks_str.split("，")[0])
                self.favorite = re.sub("\D", "", thanks_str.split("，")[1])
            except AttributeError as e:
                self.thanks = "0"
                self.favorite = "0"
            except IndexError as e:
                self.thanks = "0"
                self.favorite = "0"

    @staticmethod
    def get_live_content(p_list):
        for i_child in p_list:
            i_content = i_child.get_text()
            if i_content.startswith("现居"):
                return i_content[2:]

    def get_follow_to_list(self):
        if self.is_null is False:
            follow_to_list = "https://www.zhihu.com/people/" + self.user_id + "/following"
            driver.get(follow_to_list)
            follow_content = driver.page_source
            act_bs_object = init_bs_object(follow_content)
            all_link_list = init_href_list(act_bs_object)
            return self.get_user_list(all_link_list)
        else:
            return set([])

    def get_follow_by_list(self):
        if self.is_null is False:
            follow_to_list = "https://www.zhihu.com/people/" + self.user_id + "/followers"
            driver.get(follow_to_list)
            follow_content = driver.page_source
            act_bs_object = init_bs_object(follow_content)
            all_link_list = init_href_list(act_bs_object)
            return self.get_user_list(all_link_list)
        else:
            return set([])

    def get_user_list(self, p_list):
        user_list = []
        for i_link in p_list:
            if i_link.startswith("https://www.zhihu.com/people/"):
                user_link = i_link[29:]
                try:
                    slash_pos = user_link.index('/')
                    user_link = user_link[:slash_pos]
                except ValueError as e:
                    pass
                user_list.append(user_link)
        final_list = set(user_list)
        final_list.remove(self.user_id)
        return final_list

    def get_row_list(self):
        p_list = [self.user_id]
        if self.is_null is False:
            p_list.append(self.user_name)
            p_list.append(self.live_now)
            p_list.append(self.job)
            p_list.append(self.answers)
            p_list.append(self.asks)
            p_list.append(self.posts)
            p_list.append(self.pins)
            p_list.append(self.follow_to)
            p_list.append(self.follow_by)
            p_list.append(self.agrees)
            p_list.append(self.thanks)
            p_list.append(self.favorite)
        return p_list


def set_style(name, height, bold=False):
    style = xlwt.XFStyle()  # 初始化样式
    font = xlwt.Font()  # 为样式创建字体
    font.name = name  # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height

    style.font = font
    return style


def write_excel(p_line,p_row):
    for i in range(0,len(p_row)):
        sheet_user.write(p_line, i, p_row[i], default_style)


if __name__ == '__main__':
    url = 'https://www.zhihu.com/#signin'
    driver = init_work()
    homepage = handle_login("363261478@qq.com", "litong123", url)
    index_bs_object = init_bs_object(homepage)
    href_list = init_href_list(index_bs_object)

    workbook = xlwt.Workbook()
    sheet_user = workbook.add_sheet(u'sheet1', cell_overwrite_ok=True)
    default_style = set_style('Times New Roman', 220, True)
    row_0 = ['ID', '用户名', '居住地', '职业', '回答数', '提问数', '文章数', '想法数', '关注的人数', '被关注人数','赞同', '感谢', '收藏']
    write_excel(0, row_0)
    excel_line = 1
    start_user = "du-du-du-95"
    user_all_set = set([start_user])
    user_pop_set = set([])
    user_not_pop_set = user_all_set - user_pop_set
    sample_user = ZhUser(start_user)

    try:
        while len(user_pop_set) < 1000:
            visiting_user = user_not_pop_set.pop()
            user_pop_set.add(visiting_user)
            user_cls = ZhUser(visiting_user)
            user_all_set = user_all_set | user_cls.get_follow_by_list()
            print(str(excel_line),visiting_user,str(len(user_all_set)))
            if user_cls.is_null is False:
                write_excel(excel_line,user_cls.get_row_list())
                excel_line = excel_line + 1
            user_not_pop_set = user_all_set - user_pop_set
    finally:
        workbook.save('zhihu_user.xls')
    workbook.save('zhihu_user.xls')
    driver.close()
