# test_register.py
import random
import re
import string
import time
import pytest
from conf.logging_config import logger
from tests.pages.register_page import RegisterPage
from tests.utils.form_validation_utils import FormValidationUtils
from tests.utils.validator import generate_uscc


@pytest.mark.register
class TestRegistration:
    """用户注册测试类"""

    @pytest.mark.parametrize(
        "field, test_value, expected_tip",
        [
            # 用户名测试
            ("username", "", "请输入用户名"),

            # 密码测试
            ("password", "", "请输入密码"),
            ("password", "short", "长度在 8 到 20 个字符"),
            ("password", "toolongpasswordwithmorethan20characters", "长度在 8 到 20 个字符"),
            ("password", "alllower123!", "需同时包含大小写英文、数字及特殊字符"),
            ("password", "ALLUPPER123!", "需同时包含大小写英文、数字及特殊字符"),
            ("password", "UpperLower!", "需同时包含大小写英文、数字及特殊字符"),
            ("password", "UpperLower123", "需同时包含大小写英文、数字及特殊字符"),
            ("password", "ValidP@ss123", None),
            ("password", "P@ssw0rd", None),
            ("password", "AnotherValid123$", None),

            # 确认密码测试
            ("confirm_password", "", "请确认密码"),
            ("confirm_password", "different", "确认密码与密码不一致"),

            # 手机号测试
            ("phone", "", "请输入联系电话"),
            ("phone", "1234567890", "请输入有效的电话号码"),
            ("phone", "abcdefghijk", "请输入有效的电话号码"),
            ("phone", "13800138000", None),

            # 验证码测试
            ("verify_code_button", "", "请输入联系电话"),
            ("verify_code", "", "请输入验证码"),
            #  ("verify_code", "123456", "验证码错误"),

            # 负责人姓名测试
            ("person_in_charge", "", "请输入负责人姓名"),
            ("person_in_charge", "张三", None),  # 假设中文姓名有效

            # 身份证号测试
            ("person_in_charge_ID", "", "请输入身份证号"),
            ("person_in_charge_ID", "123456789012345", "请输入有效的身份证号"),
            # ("person_in_charge_ID", "1234567890123456789", "请输入有效的身份证号"),
            ("person_in_charge_ID", "abcdefghijklmnopqr", "请输入有效的身份证号"),
            ("person_in_charge_ID", "15010019850602008x", None),  # 有效带X的身份证号
            ("person_in_charge_ID", "150100198506020004", None),  # 有效身份证号

            # 负责人联系电话测试
            ("person_in_charge_tel", "", "请输入联系电话"),
            ("person_in_charge_tel", "1234567890", "请输入有效的电话号码"),
            ("person_in_charge_tel", "12345678aa", "请输入有效的电话号码"),
            ("person_in_charge_tel", "abcdefghijk", "请输入有效的电话号码"),
            ("person_in_charge_tel", "13800138000", None),

            # 企业名称测试（企业类型）
            ("enterprise_name", "", "请输入企业名称"),
            # # ("enterprise_name", "a" * 101, "企业名称不能超过100个字符"),
            ("enterprise_name", "有效企业名称有限公司", None),

            # 统一社会信用代码测试（企业类型）
            ("USCC", "", "请输入信用代码"),
            ("USCC", "91310104596407652E", None),
        ],
        ids=[
            "username_empty",
            "password_empty", "password_too_short", "password_too_long",
            "password_missing_upper", "password_missing_lower", "password_missing_digit", "password_missing_special",
            "password_valid_1", "password_valid_2", "password_valid_3",
            "confirm_password_empty", "confirm_password_mismatch",
            "phone_empty", "phone_invalid_format", "phone_invalid_chars", "phone_valid",
            "verify_code_button_click", "verify_code_empty",
            "person_in_charge_empty", "person_in_charge_valid",
            # "person_in_charge_ID_empty", "person_in_charge_ID_too_short", "person_in_charge_ID_too_long",
            "person_in_charge_ID_empty", "person_in_charge_ID_too_short", "person_in_charge_ID_invalid_chars",
            "person_in_charge_ID_valid_with_x", "person_in_charge_ID_valid",
            "person_in_charge_tel_empty", "person_in_charge_tel_too_short","person_in_charge_tel_invalid_format",
            "person_in_charge_tel_invalid_chars", "person_in_charge_tel_valid",
            # # "enterprise_name_empty", "enterprise_name_too_short", "enterprise_name_too_long", "enterprise_name_valid",
            "enterprise_name_empty", "enterprise_name_valid",
            # # "USCC_empty", "USCC_invalid_length", "USCC_invalid_chars", "USCC_valid", "USCC_invalid_checksum",
            "USCC_empty", "USCC_valid"
        ]
    )

    def test_field_validation(self, page, base_url, field, test_value, expected_tip):
        """测试各字段的验证逻辑，自动处理注册类型"""

        register_page = RegisterPage(page)
        register_page.navigate(base_url)

        # 获取参数字典（假设FormValidationUtils已修改为包含allow_empty）
        params = FormValidationUtils.get_form_params(field, test_value)

        # 自动确定注册类型
        fd_type = "企业" if field in ["enterprise_name", "USCC"] else "个人"
        params["fd_type"] = fd_type
        register_page.select_fd_type(fd_type)

        # 处理企业特定字段
        enterprise_name = params.pop("enterprise_name", "")
        USCC = params.pop("USCC", "")

        # 构建allow_empty参数
        allow_empty = {field}  # 允许当前测试字段为空
        # 打印所有参数
        print(f"\n当前测试字段: {field}")
        print(f"测试值: {test_value}")
        print("填写基础信息前的参数:")
        for key, value in params.items():
            print(f"  {key}: {value}")

        # 如果是企业类型，调用企业信息填写方法并传递allow_empty
        if fd_type == "企业":
            register_page.fill_enterprise_info(enterprise_name, USCC, allow_empty=allow_empty)

        # 填写基础信息并传递allow_empty
        register_page.fill_basic_info(**params, allow_empty=allow_empty)
        time.sleep(1)  # 等待表单验证
        register_page.submit_registration()

        # 针对verify_code字段的特殊处理
        if field == "verify_code" and test_value and expected_tip:
            # 当verify_code有值且期望有错误提示时，使用alert验证方法
            time.sleep(2)

            assert register_page.verify_code_alert_error(expected_tip), f"期望验证码错误提示 '{expected_tip}' 未显示"
        else:
            # 获取错误检查方法名
            error_method_name = FormValidationUtils.get_error_selector(field)

            # 动态调用错误检查方法
            error_check_method = getattr(register_page, error_method_name)
            time.sleep(2)
            if expected_tip:
                assert error_check_method(expected_tip), f"期望错误提示 '{expected_tip}' 未显示"
            else:
                assert not error_check_method(""), f"意外显示错误提示"

    @pytest.mark.parametrize(
        "field, test_value, expected_tip",
        [
            ("verify_code", "123456", "验证码错误"),  # 测试不匹配的验证码
            # ("verify_code", "abcdef", "验证码错误"),  # 测试非数字验证码
            # ("verify_code", "12345", "验证码错误"),  # 测试长度不足的验证码
            # ("verify_code", "1234567", "验证码错误"),  # 测试长度过长的验证码
        ],
        ids=[
            "verify_code_incorrect",
            # "verify_code_non_numeric",
            # "verify_code_too_short",
            # "verify_code_too_long",
        ]
    )
    def test_verify_code_error(self, page, base_url, field, test_value, expected_tip):
        """测试验证码错误场景，其他字段均为有效值"""

        register_page = RegisterPage(page)
        register_page.navigate(base_url)

        # 设置所有必要字段为有效值
        params = {
            "username": "valid_user",
            "password": "ValidP@ss123",
            "phone_number": "13800138000",
            "verify_code": test_value,  # 使用参数化的测试值
            "person_in_charge": "张三",
            "person_in_charge_ID": "15010019850602008X",
            "person_in_charge_tel": "13800138000",
        }

        # 构建test_field参数
        test_field = {field}  # 标记测试字段
        # 打印所有参数
        logger.info(f"\n当前测试字段: {field}")
        logger.info(f"测试值: {test_value}")
        logger.info("填写基础信息前的参数:")
        for key, value in params.items():
            logger.info(f"  {key}: {value}")
        # 自动确定注册类型（默认个人）
        fd_type = "个人"
        params["fd_type"] = fd_type
        register_page.select_fd_type(fd_type)

        # 填写基础信息
        register_page.fill_basic_info(**params)

        # 提交注册
        register_page.submit_registration()
        register_page.wait_send_verify_code_tip_disappear()

        # 验证验证码错误提示
        assert register_page.verify_code_alert_error(expected_tip), \
            f"期望验证码错误提示 '{expected_tip}' 未显示"

    @pytest.mark.parametrize(
        "dialog_component,fd_type",
        [
            ("close_button", "个人"),  # 个人点击关闭按钮后的预期重定向URL
            ("sure_button", "个人"),  # 个人点击确认按钮后的预期重定向URL
            ("close_button", "企业"),  # 企业点击关闭按钮后的预期重定向URL
            ("sure_button", "企业"),  # 企业点击确认按钮后的预期重定向URL
        ],
        ids=[
            "personal_verify_close_button_redirect", "personal_verify_sure_button_redirect",
            "enterprise_verify_close_button_redirect", "enterprise_verify_sure_button_redirect",
        ]
    )

    def test_landlord_registration_with_redirect(self, page, base_url, dialog_component, fd_type):
        """测试点击不同类型房东不同对话框组件后的重定向行为"""

        register_page = RegisterPage(page)
        register_page.navigate(base_url)

        # 生成随机用户名和其他必要参数
        random_username = 'test_' + ''.join(random.choices(
            string.ascii_lowercase + string.digits,
            k=random.randint(8, 12)
        ))

        # 填写完整有效的注册信息
        params = {
            "username": random_username,
            "password": "P@ssw0rd123",
            "phone_number": f"139{''.join(random.choices(string.digits, k=8))}",
            "person_in_charge": "测试用户",
            "person_in_charge_ID": "110101199001011234",
            "person_in_charge_tel": f"138{''.join(random.choices(string.digits, k=8))}",
        }

        # 设置注册类型
        params["fd_type"] = fd_type
        register_page.select_fd_type(fd_type)

        # 企业类型需要额外的信息
        if fd_type == "企业":
            # 生成企业名称和统一社会信用代码
            enterprise_name = "测试企业_" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            # 生成一个18位的随机统一社会信用代码
            USCC = ''.join(random.choices(string.digits + string.ascii_uppercase, k=17))
            USCC = f"{USCC}{generate_uscc()}"  # 添加校验位

            # 填写基础信息
            register_page.fill_basic_info(**params)

            params["enterprise_name"] = enterprise_name
            params["USCC"] = USCC

            # 填写企业额外信息
            register_page.fill_enterprise_info(enterprise_name, USCC, allow_empty=False)
        else:
            # 个人类型只需要填写基础信息
            register_page.fill_basic_info(**params)

        # 提交注册
        register_page.submit_registration()

        # 根据传入的对话框组件参数执行相应操作
        if dialog_component == "close_button":
             register_page.close_dialog_and_verify_redirect(base_url)
        elif dialog_component == "sure_button":
             register_page.click_sure_button_and_verify_redirect(base_url)
        else:
            pytest.fail(f"未知的对话框组件: {dialog_component}")

