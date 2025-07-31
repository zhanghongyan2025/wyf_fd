import re
import time
import pytest
from conf.logging_config import logger
from tests.pages.ft_manage_page import FTManagePage
from tests.pages.home_page import HomePage
from tests.pages.login_page import LoginPage
from tests.pages.ly_manage import lyManagePage
from tests.pages.room_manage_page import RoomManagePage
from tests.pages.room_register_page import RoomRegisterPage
from tests.utils.form_validation_utils import FormValidationUtils
from tests.utils.page_utils import *


# ------------------------------
# 通用Fixture：复用前置操作（修改为function作用域）
# ------------------------------
@pytest.fixture(scope="function")  # 修改为function作用域解决冲突
def ly_manage_setup(page, base_url, test_user):
    """
    楼宇管理测试的前置操作Fixture，完成用户登录并导航到楼宇管理页面。

    参数:
    page: 页面对象，用于操作浏览器页面。
    base_url: 测试的基础URL。
    test_user: 包含用户名和密码的测试用户信息。

    返回:
    lyManagePage 对象，用于后续的楼宇管理页面操作。
    """
    # 登录操作
    login_page = LoginPage(page)
    login_page.navigate(base_url)
    login_page.fill_credentials(test_user["username"], test_user["password"])
    login_page.click_login_button()

    # 验证登录是否成功，通过检查页面标题来判断
    time.sleep(2)
    # page.wait_for_url(f"{base_url}/fangdonghome")
    assert page.title() == "网约房智慧安全监管平台"

    # 导航到楼宇管理页
    home_page = HomePage(page)
    home_page.navigate_to_house_manage_page()
    ft_manage_page = FTManagePage(page)
    ft_manage_page.navigate_to_other_manage_page("楼宇管理")
    ly_manage_page = lyManagePage(page)

    # 返回楼宇管理页对象，供测试方法使用
    return ly_manage_page


@pytest.mark.room
class TestLyManage:
    """
    楼宇管理测试类，用于对楼宇管理页面的各项功能进行测试，包括基础字段验证、文件上传验证等。
    """

    @pytest.mark.parametrize("field, test_value, expected_tip", [
        ("building_name", "", "楼宇名称不能为空"),
        ("building_address", "invalid_address", "请输入有效的地址"),
        # 添加更多测试用例
    ])
    def test_base_field_validation(self, ly_manage_setup, field, test_value, expected_tip):
        """
        测试基础字段的非空及合法性验证。
        验证楼宇管理页面中各个基础字段在输入为空或不合法数据时，是否显示预期的错误提示。

        参数:
        ly_manage_setup: 楼宇管理测试的前置操作Fixture返回的页面对象。
        field: 需要测试的字段名称。
        test_value: 测试用的输入值。
        expected_tip: 预期的错误提示信息。
        """
        ly_manage_page = ly_manage_setup

        # 点击添加楼宇按钮
        ly_manage_page.click_add_building_button()

        # 填写测试数据
        ly_manage_page.fill_field(field, test_value)

        # 触发验证（例如点击保存按钮）
        ly_manage_page.click_save_button()

        # 获取实际提示信息
        actual_tip = ly_manage_page.get_field_error_tip(field)

        # 验证提示信息
        assert actual_tip == expected_tip, f"字段 {field} 的验证提示不符，预期: {expected_tip}，实际: {actual_tip}"

    def test_room_register_success_redirect(self, ly_manage_setup):
        ly_manage_page = ly_manage_setup
        ly_manage_page.add_ly("test", "新增成功")
