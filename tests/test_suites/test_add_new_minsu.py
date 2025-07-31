import re
import time
import pytest
from playwright.sync_api import expect
from conf.logging_config import logger
from tests.pages.add_new_minsu import AddNewMinsuPage
from tests.pages.ft_manage_page import FTManagePage
from tests.pages.home_page import HomePage
from tests.pages.minsu_management_page import MinsuManagementPage
from tests.pages.register_page import RegisterPage
from tests.utils.validator import generate_random_phone_number
from tests.pages.login_page import LoginPage

class FilePaths:
    """
    文件路径常量类，用于集中管理各类文件的路径，方便后续测试使用。
    """
    # 证件文件
    LARGE_ID_CARD= 'tests/data/id_card_files/large.png'
    HTML_ID_CARD= 'tests/data/id_card_files/lease.html'
    JPEG_ID_CARD= 'tests/data/id_card_files/lease.jpeg'
    JPG_ID_CARD= 'tests/data/id_card_files/lease.jpg'
    PDF_ID_CARD= 'tests/data/id_card_files/lease.pdf'
    PHP_ID_CARD= 'tests/data/id_card_files/lease.php'
    PNG_ID_CARD= 'tests/data/id_card_files/lease.png'
    PY_ID_CARD= 'tests/data/id_card_files/lease.py'
    SVG_ID_CARD= 'tests/data/id_card_files/lease.svg'
    TXT_ID_CARD= 'tests/data/id_card_files/lease.txt'
    ZIP_ID_CARD= 'tests/data/id_card_files/lease.zip'


# ------------------------------
# 通用Fixture：复用前置操作（修改为function作用域）
# ------------------------------
@pytest.fixture(scope="function")  # 修改为function作用域解决冲突
def add_new_minsu_setup(page, base_url, test_user):
    """
    房间注册测试的前置操作Fixture，其主要功能是完成用户登录并导航到房间注册页面。

    参数:
    page: 页面对象，用于操作浏览器页面。
    base_url: 测试的基础URL。
    test_user: 包含用户名和密码的测试用户信息。

    返回:
    RoomRegisterPage 对象，用于后续的房间注册页面操作。
    """
    # 登录操作
    login_page = LoginPage(page)
    login_page.navigate(base_url)
    login_page.fill_credentials(test_user["username"], test_user["password"])
    login_page.click_login_button()

    # 验证登录是否成功，通过检查页面标题来判断
    time.sleep(2)
    assert page.title() == "网约房智慧安全监管平台"

    home_page = HomePage(page)
    home_page.navigate_to_house_manage_page()
    ft_manage_page = FTManagePage(page)
    ft_manage_page.navigate_to_other_manage_page("民宿管理")
    minsu_manage_page = MinsuManagementPage(page)
    minsu_manage_page.go_to_add_minsu_page()
    return AddNewMinsuPage(page)


# ------------------------------
# 工具函数：注册页面错误提示验证
# ------------------------------
def check_add_new_minsu_error_messages(register_page, scenario, expected_errors):
    """验证注册页面多个字段的错误提示信息是否符合预期

    Args:
        register_page: 注册页面对象
        expected_errors: 预期错误字典，格式为{字段名: 预期提示文本}
    """
    for field, expected_tip in expected_errors.items():
        # 获取对应字段的错误检查方法（如 username_error）
        error_method = getattr(register_page, f"{field}_error")
        # 调用方法时传入预期错误文本作为参数
        is_match = error_method(expected_tip)
        assert is_match, (
            f"❌  场景[{scenario}], 字段 [{field}] 错误提示不匹配 - "
            f"预期: {expected_tip}, 实际未匹配"
        )


def check_add_new_minsu_alert_error_messages(register_page, scenario, expected_errors):
    """验证注册页面多个字段的弹窗错误提示是否符合预期

    Args:
        register_page: 注册页面对象
        expected_errors: 预期错误字典，格式为{字段名: 预期提示文本}
    """
    for field, expected_tip in expected_errors.items():
        # 获取对应字段的弹窗错误检查方法（如 username_alert_error）
        error_method = getattr(register_page, f"{field}_alert_error")
        # 调用方法时传入预期错误文本作为参数
        is_match = error_method(expected_tip)
        assert is_match, (
            f"❌  场景[{scenario}], 字段 [{field}] 错误提示不匹配 - "
            f"预期: {expected_tip}, 实际未匹配"
        )


# ------------------------------
# 测试类：个人/企业房东注册功能测试
# ------------------------------
@pytest.mark.register
class TestAddNewMinsu:
    """新增民宿功能测试类"""

    # # ------------------------------
    # # 场景1：民宿信息-空字段验证
    # # ------------------------------
    # minsu_empty_cases = [
    #     # (场景标识, 各字段值, 预期错误)
    #     (
    #         "all_fields_empty",
    #         {
    #             "minsu_name": "",
    #             "administrative_area": "",
    #             "detailed_address":"",
    #             "front_image": "",
    #             "back_image": ""
    #         },
    #         {
    #             "minsu_name": "民宿名称不能为空",
    #             "administrative_area": "请选择乡/镇/街道行政区划",
    #             "detailed_address": "详细地址不能为空",
    #             "front_image": "请上传负责人证件照(正面)",
    #             "back_image": "请上传负责人证件照(反面)"
    #         }
    #     )
    # ]
    # minsu_empty_ids = [case[0] for case in minsu_empty_cases]
    #
    # @pytest.mark.parametrize(
    #     "scenario, fields, expected_errors",
    #     minsu_empty_cases,
    #     ids=minsu_empty_ids
    # )
    # def test_minsu_empty_fields(
    #         self,
    #         scenario,
    #         fields,
    #         expected_errors,
    #         add_new_minsu_setup  # 将fixture作为参数传入，pytest会自动处理其依赖
    # ):
    #     """测试民宿新增页面的空字段验证逻辑"""
    #     # 直接使用fixture返回的对象，无需手动调用
    #     add_new_minsu_page = add_new_minsu_setup
    #     # 点击提交按钮
    #     add_new_minsu_page.save_minsu_info()
    #     # 验证错误提示
    #     logger.info(f"📌 民宿新增场景：执行空字段测试 [{scenario}]")
    #     check_add_new_minsu_error_messages(add_new_minsu_page, scenario, expected_errors)

    # 场景2：民宿名称长度限制测试用例
    minsu_name_length_cases = [
        # (
        #     "name_exceed_30_chars",
        #     {
        #         "minsu_name": "这是一个超过三十个字符的民宿名称用于测试长度限制情况",  # 38个字符
        #         # "minsu_name": "测试民宿",
        #         "province": "福建省",
        #         "city": "福州市",
        #         "district": "鼓楼区",
        #         "street": "鼓东街道",
        #         "detail_address": "测试详细地址123",
        #         "front_image": FilePaths.JPEG_ID_CARD,
        #         "back_image": FilePaths.JPEG_ID_CARD,
        #     },
        #     {
        #         "minsu_name": "民宿名称最多不超过30个字符"
        #     }
        # ),
        # (
        #     "name_exactly_30_chars",
        #     {
        #         "minsu_name": "这是刚好三十个字符的民宿名称测试",  # 30个字符
        #         "administrative_area": "福建省/福州市/鼓楼区/鼓东街道",
        #         "detailed_address": "测试详细地址123",
        #         "front_image": FilePaths.JPEG_ID_CARD,
        #         "back_image": FilePaths.JPEG_ID_CARD
        #     },
        #     {}  # 无错误
        # ),
        # (
        #     "name_under_30_chars",
        #     {
        #         "minsu_name": "短名称民宿",  # 6个字符
        #         "administrative_area": "完整的行政区划/省/市/区/乡镇",
        #         "detailed_address": "测试详细地址123",
        #         "front_image": FilePaths.JPEG_ID_CARD,
        #         "back_image": FilePaths.JPEG_ID_CARD
        #     },
        #     {}  # 无错误
        # )

        # 场景7：民宿添加成功测试用例
        (
            "name_exceed_30_chars",
            {
                "minsu_name": "测试民宿",
                "province": "山东省",
                "city": "潍坊市",
                "district": "坊子区",
                "street": "凤凰街道",
                "detail_address": "测试详细地址123",
                "front_image": FilePaths.JPEG_ID_CARD,
                "back_image": FilePaths.JPEG_ID_CARD,
            },
            {
                "success": "保存成功"
            }
        ),
    ]
    minsu_name_length_ids = [case[0] for case in minsu_name_length_cases]

    @pytest.mark.parametrize(
        "scenario, fields, expected_errors",
        minsu_name_length_cases,
        ids=minsu_name_length_ids
    )
    def test_minsu_name_length(
            self,
            scenario,
            fields,
            expected_errors,
            add_new_minsu_setup  # 将fixture作为参数传入，pytest会自动处理其依赖
    ):
        """测试民宿名称长度限制"""
        # 直接使用fixture返回的对象，无需手动调用
        add_new_minsu_page = add_new_minsu_setup
        add_new_minsu_page.add_new_minsu(**fields)
        add_new_minsu_page.save_minsu_info()
        # 验证错误提示
        logger.info(f"📌 民宿新增场景：执行民宿名称长度测试场景 [{scenario}]")
        check_add_new_minsu_error_messages(add_new_minsu_page, scenario, expected_errors)

    # # 场景3：行政区划选择完整性测试用例
    # minsu_admin_area_cases = [
    #     (
    #         "admin_area_only_province",
    #         {
    #             "minsu_name": "测试民宿名称",
    #             "administrative_area": "仅选择省份",
    #             "detailed_address": "测试详细地址123",
    #             "front_image": FilePaths.JPEG_ID_CARD,
    #             "back_image": FilePaths.JPEG_ID_CARD
    #         },
    #         {
    #             "administrative_area": "请选择乡/镇/街道行政区划"
    #         }
    #     ),
    #     (
    #         "admin_area_province_city",
    #         {
    #             "minsu_name": "测试民宿名称",
    #             "administrative_area": "选择到省市",
    #             "detailed_address": "测试详细地址123",
    #             "front_image": FilePaths.JPEG_ID_CARD,
    #             "back_image": FilePaths.JPEG_ID_CARD
    #         },
    #         {
    #             "administrative_area": "请选择乡/镇/街道行政区划"
    #         }
    #     ),
    #     (
    #         "admin_area_complete",
    #         {
    #             "minsu_name": "测试民宿名称",
    #             "administrative_area": "完整的行政区划/省/市/区/乡镇",
    #             "detailed_address": "测试详细地址123",
    #             "front_image": FilePaths.JPEG_ID_CARD,
    #             "back_image": FilePaths.JPEG_ID_CARD
    #         },
    #         {}  # 无错误
    #     )
    # ]
    # minsu_admin_area_ids = [case[0] for case in minsu_admin_area_cases]

    # # 场景4：证件照大小限制测试用例
    # minsu_image_size_cases = [
    #     (
    #         "front_image_15mb",
    #         {
    #             "minsu_name": "测试民宿名称",
    #             "administrative_area": "完整的行政区划/省/市/区/乡镇",
    #             "detailed_address": "测试详细地址123",
    #             "front_image": "15mb_front.jpg",  # 模拟15MB文件
    #             "back_image": "5mb_back.png"
    #         },
    #         {
    #             "front_image": "上传头像图片大小不能超过 10 MB!"
    #         }
    #     ),
    #     (
    #         "back_image_20mb",
    #         {
    #             "minsu_name": "测试民宿名称",
    #             "administrative_area": "完整的行政区划/省/市/区/乡镇",
    #             "detailed_address": "测试详细地址123",
    #             "front_image": "5mb_front.jpg",
    #             "back_image": "20mb_back.png"  # 模拟20MB文件
    #         },
    #         {
    #             "back_image": "上传头像图片大小不能超过 10 MB!"
    #         }
    #     ),
    #     (
    #         "both_images_5mb",
    #         {
    #             "minsu_name": "测试民宿名称",
    #             "administrative_area": "完整的行政区划/省/市/区/乡镇",
    #             "detailed_address": "测试详细地址123",
    #             "front_image": "5mb_front.jpg",
    #             "back_image": "5mb_back.png"
    #         },
    #         {}  # 无错误
    #     )
    # ]
    # minsu_image_size_ids = [case[0] for case in minsu_image_size_cases]
    #
    # # 场景5：证件照格式限制测试用例
    # minsu_image_format_cases = [
    #     (
    #         "front_image_pdf",
    #         {
    #             "minsu_name": "测试民宿名称",
    #             "administrative_area": "完整的行政区划/省/市/区/乡镇",
    #             "detailed_address": "测试详细地址123",
    #             "front_image": "invalid_front.pdf",  # 无效格式
    #             "back_image": "valid_back.png"
    #         },
    #         {
    #             "front_image": "文件格式不正确, 请上传jpg/jpeg/png图片格式文件!"
    #         }
    #     ),
    #     (
    #         "back_image_txt",
    #         {
    #             "minsu_name": "测试民宿名称",
    #             "administrative_area": "完整的行政区划/省/市/区/乡镇",
    #             "detailed_address": "测试详细地址123",
    #             "front_image": "valid_front.jpg",
    #             "back_image": "invalid_back.txt"  # 无效格式
    #         },
    #         {
    #             "back_image": "文件格式不正确, 请上传jpg/jpeg/png图片格式文件!"
    #         }
    #     ),
    #     (
    #         "front_image_jpeg_back_image_png",
    #         {
    #             "minsu_name": "测试民宿名称",
    #             "administrative_area": "完整的行政区划/省/市/区/乡镇",
    #             "detailed_address": "测试详细地址123",
    #             "front_image": "valid_front.jpeg",  # 有效格式
    #             "back_image": "valid_back.png"  # 有效格式
    #         },
    #         {}  # 无错误
    #     )
    # ]
    # minsu_image_format_ids = [case[0] for case in minsu_image_format_cases]
