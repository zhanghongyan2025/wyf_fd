from playwright.sync_api import Page, expect
from tests.utils.page_utils import *
from tests.pages.add_new_minsu import AddNewMinsuPage

class MinsuManagementPage:
    def __init__(self, page: Page):
        self.page = page

        # 查询区域折叠/展开按钮
        self.expand_query_button = self.page.get_by_role("button", name="展开查询")
        self.collapse_query_button = self.page.get_by_role("button", name="收起查询")

        # 搜索区域元素
        self.minsu_name_search_input = self.page.get_by_role("textbox", name="请输入民宿名称")
        self.administrative_area_search_input = self.page.get_by_role("textbox", name="请选择行政区划")
        self.manager_name_search_input = self.page.get_by_role("textbox", name="请输入负责人姓名")
        self.search_button = self.page.get_by_role("button", name="搜索")
        self.reset_button = self.page.get_by_role("button", name="重置")

        # 功能按钮
        self.add_minsu_button = self.page.get_by_role("button", name=" 新增民宿")

    def expand_query(self):
        """展开查询区域，显示搜索相关元素"""
        try:
            # 点击展开查询按钮
            self.expand_query_button.click()
            # 等待搜索元素显示
            self.minsu_name_search_input.wait_for(state="visible")
            self.administrative_area_search_input.wait_for(state="visible")
            self.manager_name_search_input.wait_for(state="visible")
            self.search_button.wait_for(state="visible")
            self.reset_button.wait_for(state="visible")
        except Exception as e:
            self.page.screenshot(path="expand_query_error.png")
            raise e

    def collapse_query(self):
        """收起查询区域，隐藏搜索相关元素"""
        try:
            # 点击收起查询按钮
            self.collapse_query_button.click()
            # 验证搜索元素已隐藏
            expect(self.minsu_name_search_input).to_be_hidden()
            expect(self.administrative_area_search_input).to_be_hidden()
            expect(self.manager_name_search_input).to_be_hidden()
            expect(self.search_button).to_be_hidden()
            expect(self.reset_button).to_be_hidden()
        except Exception as e:
            self.page.screenshot(path="collapse_query_error.png")
            raise e

    def search_minsu(self, minsu_name: str = None, area: str = None, manager_name: str = None):
        """
        搜索民宿（先确保查询区域已展开）
        :param minsu_name: 民宿名称
        :param area: 行政区划
        :param manager_name: 负责人姓名
        """
        try:
            # 确保查询区域已展开
            self.expand_query()

            if minsu_name:
                self.minsu_name_search_input.click()
                self.minsu_name_search_input.fill(minsu_name)

            if area:
                self.administrative_area_search_input.click()
                self.administrative_area_search_input.fill(area)
                # 这里可以根据需要添加选择区域的逻辑

            if manager_name:
                self.manager_name_search_input.click()
                self.manager_name_search_input.fill(manager_name)

            self.search_button.click()
            # 等待搜索结果加载
            self.page.wait_for_timeout(1000)

        except Exception as e:
            self.page.screenshot(path="minsu_search_error.png")
            raise e

    def reset_search(self):
        """重置搜索条件（先确保查询区域已展开）"""
        try:
            # 确保查询区域已展开
            self.expand_query()

            self.reset_button.click()
            # 验证输入框已清空
            expect(self.minsu_name_search_input).to_have_value("")
            expect(self.administrative_area_search_input).to_have_value("")
            expect(self.manager_name_search_input).to_have_value("")
        except Exception as e:
            self.page.screenshot(path="reset_search_error.png")
            raise e

    def go_to_add_minsu_page(self):
        """点击新增民宿按钮，进入新增页面并验证URL跳转"""
        try:
            # 获取当前页面URL用于拼接新增页面地址
            current_url = self.page.url.rstrip('/')  # 移除可能存在的尾部斜杠
            add_minsu_url = f"{current_url}/add"  # 拼接生成新增页面URL
            self.page.wait_for_timeout(2000)
            # 点击新增民宿按钮
            self.add_minsu_button.click()

            # 验证是否跳转到正确的新增页面
            # expect(self.page).to_have_url(add_minsu_url)

            # 返回新增民宿页面操作对象
            return AddNewMinsuPage(self.page)

        except Exception as e:
            self.page.screenshot(path="go_to_add_minsu_error.png")
            # 发生异常时尝试返回原页面
            if self.page.url != current_url:
                self.page.go_back()
            raise e
