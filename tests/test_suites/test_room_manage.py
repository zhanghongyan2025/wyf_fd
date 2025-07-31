import re
import time

import pytest
from conf.logging_config import logger
from tests.pages.ft_manage_page import FTManagePage
from tests.pages.home_page import HomePage
from tests.pages.login_page import LoginPage
from tests.pages.room_manage_page import RoomManagePage
from tests.pages.room_register_page import RoomRegisterPage
from tests.utils.form_validation_utils import FormValidationUtils


# 假设这些目录存在且包含图片文件
LARGE_PROPERTY_CERTIFICATE = 'tests/data/evidence_files/large.png'
HTML_PROPERTY_CERTIFICATE = 'tests/data/evidence_files/lease.html'
JPEG_PROPERTY_CERTIFICATE = 'tests/data/evidence_files/lease.jpeg'
JPG_PROPERTY_CERTIFICATE = 'tests/data/evidence_files/lease.jpg'
PDF_PROPERTY_CERTIFICATE = 'tests/data/evidence_files/lease.pdf'
PHP_PROPERTY_CERTIFICATE = 'tests/data/evidence_files/lease.php'
PNG_PROPERTY_CERTIFICATE = 'tests/data/evidence_files/lease.png'
PY_PROPERTY_CERTIFICATE = 'tests/data/evidence_files/lease.py'
SVG_PROPERTY_CERTIFICATE = 'tests/data/evidence_files/lease.svg'
TXT_PROPERTY_CERTIFICATE = 'tests/data/evidence_files/lease.txt'
ZIP_PROPERTY_CERTIFICATE = 'tests/data/evidence_files/lease.zip'


BEDROOM_FILES = 'tests/data/bedroom_files'
LIVING_ROOM_FILES = 'tests/data/livingroom_files'
KITCHEN_FILES = 'tests/data/kitchen_files'
BATHROOM_FILES = 'tests/data/bathroom_files'

pattern = r'multi_.+?_certificate'

@pytest.mark.room
class TestRoomRegistration:
    """房间信息注册测试类"""

    @pytest.mark.parametrize(
        "field, test_value, expected_tip",
        [
            # 基本信息
            ("room_name", "", "房间名称不能为空"),
            ("ms_name", "", "请选择民宿"),
            ("floor", "", "请选择楼层"),
            ("ly_name", "", "请选择楼宇"),
            ("room_type", "", "请选择房间类型"),

            # 数量信息
            ("bedroom_number", "", "请输入卧室数量"),
            ("living_room_number", "", "请输入客厅数量"),
            ("kitchen_number", "", "请输入厨房数量"),
            ("bathroom_number", "", "请输入卫生间数量"),
            ("area", "", "房型面积(㎡)不能为空"),
            ("bed_number", "", "床数量不能为空"),
            ("max_occupancy", "", "最大住人数不能为空"),

            # 设施选择
            ("parking", "", "请选择是否有车位"),
            ("balcony", "", "请选择是否有阳台"),
            ("window", "", "请选择是否有窗户"),
            ("tv", "", "请选择电视机"),
            ("projector", "", "请选择投影仪"),
            ("washing_machine", "", "请选择洗衣机"),
            ("clothes_steamer", "", "请选择挂烫机"),
            ("water_heater", "", "请选择热水器"),
            ("hair_dryer", "", "请选择吹风机"),
            ("fridge", "", "请选择冰箱"),
            ("stove", "", "请选择炉灶"),
            ("toilet", "", "请选择便器"),

            # 证件上传
            ("property_type", "自有", "请上传产权证明"),
            ("property_type", "租赁", "请上传租赁证明"),
            ("property_type", "共有", "请上传共有产权证明"),
        ],
        ids=[
            "room_name_empty",
            "ms_not_selected", "floor_not_selected", "ly_not_selected",
            "room_type_not_selected",
            "bedroom_number_empty", "living_room_number_empty", "kitchen_number_empty", "bathroom_number_empty",
            "area_empty", "bed_number_empty", "max_guests_empty",
            "parking_not_selected", "balcony_not_selected", "window_not_selected",
            "tv_not_selected", "projector_not_selected", "washing_machine_not_selected",
            "clothes_steamer_not_selected", "water_heater_not_selected", "hair_dryer_not_selected",
            "fridge_not_selected", "stove_not_selected", "toilet_not_selected",
            "property_certificate_not_uploaded_owned", "property_certificate_not_uploaded_leased","property_certificate_not_uploaded_shared"
        ]
    )

    def test_room_field_validation(self, page, base_url, test_user, field, test_value, expected_tip):
        """测试房间信息各字段的验证逻辑"""
        """测试房间注册功能"""
        login_page = LoginPage(page)
        login_page.navigate(base_url)
        login_page.fill_credentials(test_user["username"], test_user["password"])
        login_page.click_login_button()

        # 验证登录成功后的跳转
        page.wait_for_url(f"{base_url}/fangdonghome")
        assert page.title() == "网约房智慧安全监管平台"
        home_page = HomePage(page)
        home_page.navigate_to_house_manage_page()
        ft_managePage_page = FTManagePage(page)
        ft_managePage_page.navigate_to_other_manage_page("房间管理")
        room_manage_page = RoomManagePage(page)
        room_manage_page.navigate_to_register()

        # 获取表单参数
        params = FormValidationUtils.get_form_params("room", field, test_value)
        logger.info(f"params: {params}")
        if field == "property_type":
           test_fields = "property_certificate"  # 当前测试字段
        else:
            test_fields = field
        room_register_page = RoomRegisterPage(page)
        room_register_page.fill_room_info(test_fields=test_fields, **params)
        room_register_page.submit_form()
        time.sleep(1)

        if field == "property_type":
            assert room_register_page.property_certificate_empty_error(expected_tip)
        else:
            # 获取错误检查方法名 - 从集合中获取唯一元素
            error_method_name = FormValidationUtils.get_error_selector("room", test_fields)
            # 动态调用错误检查方法
            error_check_method = getattr(room_register_page, error_method_name)
            assert error_check_method(expected_tip)


    @pytest.mark.parametrize(
        "field, test_value, expected_tip",
        [

            ("property_type", "自有", "产权证明"),
            ("property_type", "租赁", "租赁证明"),
            ("property_type", "共有", "共有产权证明"),

        ],
        ids=[
            "property_type_owned",
            "property_type_leased",
            "property_type_co_ownership",
        ]
    )

    def test_room_property_type_validation(self, page, base_url, test_user, field, test_value, expected_tip):
        """测试房间信息各字段的验证逻辑"""
        """测试房间注册功能"""
        login_page = LoginPage(page)
        login_page.navigate(base_url)
        login_page.fill_credentials(test_user["username"], test_user["password"])
        login_page.click_login_button()

        # 验证登录成功后的跳转
        page.wait_for_url(f"{base_url}/fangdonghome")
        assert page.title() == "网约房智慧安全监管平台"
        home_page = HomePage(page)
        home_page.navigate_to_house_manage_page()
        ft_managePage_page = FTManagePage(page)
        ft_managePage_page.navigate_to_other_manage_page("房间管理")
        room_manage_page = RoomManagePage(page)
        room_manage_page.navigate_to_register()

        params = FormValidationUtils.get_form_params("room", field, test_value)
        test_fields = field # 允许当前测试字段为空


        room_register_page = RoomRegisterPage(page)
        room_register_page.fill_room_info(test_fields=test_fields, **params)

        room_register_page.submit_form()
        # 获取错误检查方法名
        error_method_name = FormValidationUtils.get_error_selector("room", field)

        # 动态调用错误检查方法
        error_check_method = getattr(room_register_page, error_method_name)
        assert error_check_method(test_value)


    @pytest.mark.parametrize(
        "field, test_value, expected_tip",
        [
            # 空文件
            ("property_certificate", '', ""),

            # 超过10M的文件
            ("property_certificate", LARGE_PROPERTY_CERTIFICATE, "上传文件大小不能超过 10 MB!"),

            # 上传不支持的文件类型
            ("property_certificate", HTML_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("property_certificate", PHP_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("property_certificate", PY_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("property_certificate", SVG_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("property_certificate",  TXT_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("property_certificate", ZIP_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),

            # 上传多个文件
            ("property_certificate",  JPEG_PROPERTY_CERTIFICATE , "上传文件数量不能超过 1 个!"),

        ],
        ids=[
            "empty_property_certificate",
             "large_property_certificate",
             "html_property_certificate", "php_property_certificate", "py_property_certificate", "svg_property_certificate","txt_property_certificate", "zip_property_certificate",
            "multi_property_certificate",
        ]
    )

    def test_room_field_validation(self, request, page, base_url, test_user, field, test_value, expected_tip):
        """测试房间信息各字段的验证逻辑"""

        # 登录
        login_page = LoginPage(page)
        login_page.navigate(base_url)
        login_page.fill_credentials(test_user["username"], test_user["password"])
        login_page.click_login_button()

        # 验证登录成功
        page.wait_for_url(f"{base_url}/fangdonghome")
        assert page.title() == "网约房智慧安全监管平台"

        # 导航到房间注册页面
        home_page = HomePage(page)
        home_page.navigate_to_house_manage_page()
        ft_managePage_page = FTManagePage(page)
        ft_managePage_page.navigate_to_other_manage_page("房间管理")
        room_manage_page = RoomManagePage(page)
        room_manage_page.navigate_to_register()

        # 获取表单参数
        params = FormValidationUtils.get_form_params("room", field, test_value)
        logger.info(f"params: {params}")
        test_fields = field

        # 注册房间
        room_register_page = RoomRegisterPage(page)
        current_test_id = request.node.name
        logger.info(f"当前测试用例ID: {current_test_id}")
        logger.info(f"pytest: {current_test_id}")

        if current_test_id and "multi_property_certificate" in current_test_id:
           room_register_page.upload_property_certificate(params.get("property_type"), test_value, test_fields=test_fields)

        if test_value == '':
            property_type_mapping = {
                "自有": "请上传产权证明",
                "租赁": "请上传租赁证明",
                "共有": "请上传共有产权证明"
            }

            # 遍历所有property_type选项
            for property_type, certificate_hint in property_type_mapping.items():
                # 复制params字典并设置当前property_type
                new_params = params.copy()
                new_params["property_type"] = property_type
                new_params.pop("property_certificate", None)
                logger.info(f"当前测试的property_type: {property_type}")
                logger.info(f"当前测试的certificate_hint: {certificate_hint}")
                room_register_page.fill_room_info(test_fields=test_fields, **new_params)
                room_register_page.submit_form()
                assert room_register_page.property_certificate_empty_error(certificate_hint)
        else:

            room_register_page.upload_property_certificate(params.get("property_type"), test_value, test_fields=test_fields)

            # 提交表单
            room_register_page.submit_form()

            assert room_register_page.property_certificate_error(expected_tip)

    @pytest.mark.parametrize(
        "field, test_value, expected_tip",
        [
            # # 超过10M的文件
            ("fire_safety_certificate", LARGE_PROPERTY_CERTIFICATE, "上传文件大小不能超过 10 MB!"),

            # 上传不支持的文件类型
            ("fire_safety_certificate", HTML_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("fire_safety_certificate", PHP_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("fire_safety_certificate", PY_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("fire_safety_certificate", SVG_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("fire_safety_certificate",  TXT_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("fire_safety_certificate", ZIP_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),

            ## 上传多个文件
            ("fire_safety_certificate",  JPEG_PROPERTY_CERTIFICATE , "上传文件数量不能超过 1 个!"),

        ],
        ids=[
            "large_fire_safety_certificate",
            "html_fire_safety_certificate", "php_fire_safety_certificate", "py_fire_safety_certificate", "svg_fire_safety_certificate","txt_fire_safety_certificate", "zip_fire_safety_certificate",
            "multi_fire_safety_certificate",
        ]
    )

    def test_room_field_validation(self, request, page, base_url, test_user, field, test_value, expected_tip):
        """测试房间信息各字段的验证逻辑"""

        # 登录
        login_page = LoginPage(page)
        login_page.navigate(base_url)
        login_page.fill_credentials(test_user["username"], test_user["password"])
        login_page.click_login_button()

        # 验证登录成功
        page.wait_for_url(f"{base_url}/fangdonghome")
        assert page.title() == "网约房智慧安全监管平台"

        # 导航到房间注册页面
        home_page = HomePage(page)
        home_page.navigate_to_house_manage_page()
        ft_managePage_page = FTManagePage(page)
        ft_managePage_page.navigate_to_other_manage_page("房间管理")
        room_manage_page = RoomManagePage(page)
        room_manage_page.navigate_to_register()

        # 获取表单参数
        params = FormValidationUtils.get_form_params("room", field, test_value)
        logger.info(f"params: {params}")
        test_fields = field

        # 注册房间
        room_register_page = RoomRegisterPage(page)
        current_test_id = request.node.name
        logger.info(f"当前测试zi: {current_test_id}")
        logger.info(f"当前测试用例ID: {current_test_id}")
        logger.info(f"pytest: {current_test_id}")
        if current_test_id and re.search(pattern, current_test_id) :
            room_register_page.upload_fire_safety_certificate(test_value, test_fields=test_fields)

        room_register_page.upload_fire_safety_certificate(test_value, test_fields=test_fields)


        # 获取错误检查方法名
        error_method_name = FormValidationUtils.get_error_selector("room", field)

        # 动态调用错误检查方法
        error_check_method = getattr(room_register_page, error_method_name)
        assert error_check_method(expected_tip)


    @pytest.mark.parametrize(
        "field, test_value, expected_tip",
        [
            # # 超过10M的文件 for Public Security
            ("public_security_registration_form", LARGE_PROPERTY_CERTIFICATE, "上传文件大小不能超过 10 MB!"),

            # 上传不支持的文件类型
            ("public_security_registration_form", HTML_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("public_security_registration_form", PHP_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("public_security_registration_form", PY_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("public_security_registration_form", SVG_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("public_security_registration_form",  TXT_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),
            ("public_security_registration_form", ZIP_PROPERTY_CERTIFICATE, "文件格式不正确, 请上传pdf/jpg/jpeg/png格式文件!"),

            ## 上传多个文件
            ("public_security_registration_form",  JPEG_PROPERTY_CERTIFICATE , "上传文件数量不能超过 1 个!"),

        ],
        ids=[
            "large_public_security_registration_form_certificate",
            "html_public_security_registration_form_certificate", "php_public_security_registration_form_certificate", "py_public_security_registration_form_certificate", "svg_public_security_registration_form_certificate","txt_public_security_registration_form_certificate", "zip_public_security_registration_form_certificate",
            "multi_public_security_registration_form_certificate",
        ]
    )


    def test_room_field_validation(self, request, page, base_url, test_user, field, test_value, expected_tip):
        """测试房间信息各字段的验证逻辑"""

        # 登录
        login_page = LoginPage(page)
        login_page.navigate(base_url)
        login_page.fill_credentials(test_user["username"], test_user["password"])
        login_page.click_login_button()

        # 验证登录成功
        page.wait_for_url(f"{base_url}/fangdonghome")
        assert page.title() == "网约房智慧安全监管平台"

        # 导航到房间注册页面
        home_page = HomePage(page)
        home_page.navigate_to_house_manage_page()
        ft_managePage_page = FTManagePage(page)
        ft_managePage_page.navigate_to_other_manage_page("房间管理")
        room_manage_page = RoomManagePage(page)
        room_manage_page.navigate_to_register()

        # 获取表单参数
        params = FormValidationUtils.get_form_params("room", field, test_value)
        # logger.info(f"params: {params}")
        test_fields = field

        # 注册房间
        room_register_page = RoomRegisterPage(page)
        current_test_id = request.node.name
        logger.info(f"当前测试zi: {current_test_id}")
        logger.info(f"当前测试用例ID: {current_test_id}")
        logger.info(f"pytest: {current_test_id}")
        if current_test_id and re.search(pattern, current_test_id) :
            room_register_page.upload_public_security_registration_form(test_value, test_fields=test_fields)

        room_register_page.upload_public_security_registration_form(test_value, test_fields=test_fields)


        # 获取错误检查方法名
        error_method_name = FormValidationUtils.get_error_selector("room", field)

        # 动态调用错误检查方法
        error_check_method = getattr(room_register_page, error_method_name)
        assert error_check_method(expected_tip)


    @pytest.mark.parametrize(
        "field, test_value, expected_tip",
        [

            ("living_room_number", "1,,,", "请输入客厅数量"),
            ("kitchen_number", "1,1,,", "请输入厨房数量"),
            ("bathroom_number", "1,1,1,", "请输入卫生间数量"),

        ],
        ids=[
            "only_bedroom_number",
            "only_bedroom_living_room_number",
            "missing_bedroom_number",
        ]
    )


    def test_room_field_validation(self, request, page, base_url, test_user, field, test_value, expected_tip):
        """测试房间信息各字段的验证逻辑"""

        # 登录
        login_page = LoginPage(page)
        login_page.navigate(base_url)
        login_page.fill_credentials(test_user["username"], test_user["password"])
        login_page.click_login_button()

        # 验证登录成功
        page.wait_for_url(f"{base_url}/fangdonghome")
        assert page.title() == "网约房智慧安全监管平台"

        # 导航到房间注册页面
        home_page = HomePage(page)
        home_page.navigate_to_house_manage_page()
        ft_managePage_page = FTManagePage(page)
        ft_managePage_page.navigate_to_other_manage_page("房间管理")
        room_manage_page = RoomManagePage(page)
        room_manage_page.navigate_to_register()

        # 获取表单参数
        params = FormValidationUtils.get_form_params("room", field, test_value)
        logger.info(f"params: {params}")
        test_fields = field
        logger.info(f"当前测试: {test_fields}")
        # # 注册房间
        room_register_page = RoomRegisterPage(page)
        room_register_page.fill_room_info(test_fields=test_fields, **params)

        # 获取错误检查方法名
        error_method_name = FormValidationUtils.get_error_selector("room", field)

        # 动态调用错误检查方法
        error_check_method = getattr(room_register_page, error_method_name)
        assert error_check_method(expected_tip)


    @pytest.mark.parametrize(
        "field, test_value, expected_tip",
        [

            ("living_room_number", "1,,,", "请输入客厅数量"),
            ("kitchen_number", "1,1,,", "请输入厨房数量"),
            ("bathroom_number", "1,1,1,", "请输入卫生间数量"),

        ],
        ids=[
            "only_bedroom_number",
            "only_bedroom_living_room_number",
            "missing_bedroom_number",
        ]
    )


    def test_room_field_validation(self, request, page, base_url, test_user, field, test_value, expected_tip):
        """测试房间信息各字段的验证逻辑"""

        # 登录
        login_page = LoginPage(page)
        login_page.navigate(base_url)
        login_page.fill_credentials(test_user["username"], test_user["password"])
        login_page.click_login_button()

        # 验证登录成功
        page.wait_for_url(f"{base_url}/fangdonghome")
        assert page.title() == "网约房智慧安全监管平台"

        # 导航到房间注册页面
        home_page = HomePage(page)
        home_page.navigate_to_house_manage_page()
        ft_managePage_page = FTManagePage(page)
        ft_managePage_page.navigate_to_other_manage_page("房间管理")
        room_manage_page = RoomManagePage(page)
        room_manage_page.navigate_to_register()

        # 获取表单参数
        params = FormValidationUtils.get_form_params("room", field, test_value)
        logger.info(f"params: {params}")
        test_fields = field
        logger.info(f"当前测试: {test_fields}")
        # # 注册房间
        room_register_page = RoomRegisterPage(page)
        room_register_page.fill_room_info(test_fields=test_fields, **params)

        # 获取错误检查方法名
        error_method_name = FormValidationUtils.get_error_selector("room", field)

        # 动态调用错误检查方法
        error_check_method = getattr(room_register_page, error_method_name)
        assert error_check_method(expected_tip)

    @pytest.mark.parametrize(
        "field, test_value, expected_tip",
        [

            ("living_room_number", "1,,,", "请输入客厅数量"),
            ("kitchen_number", "1,1,,", "请输入厨房数量"),
            ("bathroom_number", "1,1,1,", "请输入卫生间数量"),

        ],
        ids=[
            "only_bedroom_number",
            "only_bedroom_living_room_number",
            "missing_bedroom_number",
        ]
    )


    def test_room_field_validation(self, request, page, base_url, test_user, field, test_value, expected_tip):
        """测试房间信息各字段的验证逻辑"""

        # 登录
        login_page = LoginPage(page)
        login_page.navigate(base_url)
        login_page.fill_credentials(test_user["username"], test_user["password"])
        login_page.click_login_button()

        # 验证登录成功
        page.wait_for_url(f"{base_url}/fangdonghome")
        assert page.title() == "网约房智慧安全监管平台"

        # 导航到房间注册页面
        home_page = HomePage(page)
        home_page.navigate_to_house_manage_page()
        ft_managePage_page = FTManagePage(page)
        ft_managePage_page.navigate_to_other_manage_page("房间管理")
        room_manage_page = RoomManagePage(page)
        room_manage_page.navigate_to_register()

        # 获取表单参数
        params = FormValidationUtils.get_form_params("room", field, test_value)
        logger.info(f"params: {params}")
        test_fields = field
        logger.info(f"当前测试: {test_fields}")
        # # 注册房间
        room_register_page = RoomRegisterPage(page)
        room_register_page.fill_room_info(test_fields=test_fields, **params)

        # 获取错误检查方法名
        error_method_name = FormValidationUtils.get_error_selector("room", field)

        # 动态调用错误检查方法
        error_check_method = getattr(room_register_page, error_method_name)
        assert error_check_method(expected_tip)



