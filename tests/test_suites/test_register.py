import re
import time
import pytest
from playwright.sync_api import expect
from conf.logging_config import logger
from tests.utils.form_validation_utils import FormValidationUtils
from tests.utils.page_utils import check_page_title
from tests.pages.register_page import RegisterPage
from tests.utils.validator import generate_random_phone_number
from tests.pages.login_page import LoginPage


# ------------------------------
# 工具函数：注册页面错误提示验证
# ------------------------------
def check_register_error_messages(register_page, scenario, expected_errors):
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


def check_register_alert_error_messages(register_page, scenario, expected_errors):
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
class TestRegister:
    """注册功能测试类，区分个人/企业房东类型的字段差异验证"""
    #
    # # ------------------------------
    # # 场景1：个人房东-空字段验证
    # # ------------------------------
    # personal_empty_cases = [
    #     # (场景标识, 各字段值, 预期错误)
    #     (
    #         "personal_all_empty",
    #         {
    #             "username": "",
    #             "password": "",
    #             "confirm_password": "",
    #             "phone_number": "",
    #             "verify_code": "",
    #             "person_in_charge": "",
    #             "person_in_charge_ID": "",
    #             "person_in_charge_tel": ""
    #         },
    #         {
    #             "username": "请输入用户名",
    #             "password": "请输入密码",
    #             "confirm_password": "请确认密码",
    #             "phone_number": "请输入联系电话",
    #             "verify_code": "请输入验证码",
    #             "person_in_charge": "请输入负责人姓名",
    #             "person_in_charge_ID": "请输入身份证号",
    #             "person_in_charge_tel": "请输入联系电话"
    #         }
    #     )
    # ]
    # personal_empty_ids = [case[0] for case in personal_empty_cases]
    #
    # @pytest.mark.parametrize(
    #     "scenario, fields, expected_errors",
    #     personal_empty_cases,
    #     ids=personal_empty_ids
    # )
    # def test_personal_empty_fields(
    #         self,
    #         page,
    #         base_url,
    #         scenario,
    #         fields,
    #         expected_errors
    # ):
    #     """测试个人房东类型下的空字段验证逻辑"""
    #     register_page = RegisterPage(page)
    #     register_page.navigate(base_url)
    #     register_page.fill_basic_info(**fields)
    #     register_page.submit_registration()
    #     time.sleep(1)
    #
    #     logger.info(f"📌 个人房东场景：执行空字段测试 [{scenario}]")
    #     check_register_error_messages(register_page, scenario, expected_errors)
    #
    # # ------------------------------
    # # 场景2：企业房东-空字段验证
    # # ------------------------------
    # enterprise_empty_cases = [
    #     # (场景标识, 各字段值, 预期错误)
    #     (
    #         "enterprise_all_empty",
    #         {
    #             "username": "",
    #             "password": "",
    #             "confirm_password": "",
    #             "phone_number": "",
    #             "verify_code": "",
    #             "person_in_charge": "",
    #             "person_in_charge_ID": "",
    #             "person_in_charge_tel": "",
    #             "enterprise_name": "",
    #             "USCC": ""
    #         },
    #         {
    #             "username": "请输入用户名",
    #             "password": "请输入密码",
    #             "confirm_password": "请确认密码",
    #             "phone_number": "请输入联系电话",
    #             "verify_code": "请输入验证码",
    #             "legal_person_in_charge": "请输入法定负责人姓名",
    #             "legal_person_in_charge_ID": "请输入身份证号",
    #             "legal_person_in_charge_tel": "请输入联系电话",
    #             "enterprise_name": "请输入企业名称",
    #             "USCC": "请输入信用代码"
    #         }
    #     ),
    # ]
    # enterprise_empty_ids = [case[0] for case in enterprise_empty_cases]
    #
    # @pytest.mark.parametrize(
    #     "scenario, fields, expected_errors",
    #     enterprise_empty_cases,
    #     ids=enterprise_empty_ids
    # )
    # def test_enterprise_empty_fields(
    #         self,
    #         page,
    #         base_url,
    #         scenario,
    #         fields,
    #         expected_errors
    # ):
    #     """测试企业房东类型下的空字段验证逻辑"""
    #     register_page = RegisterPage(page)
    #     register_page.navigate(base_url)
    #
    #     # 切换到企业房东类型
    #     register_page.select_fd_type("企业")
    #     expect(register_page.enterprise).to_be_checked()
    #
    #     # 填充表单字段
    #     enterprise_name = fields.pop("enterprise_name")
    #     USCC = fields.pop("USCC")
    #     register_page.fill_basic_info(**fields)
    #     register_page.fill_enterprise_info(enterprise_name, USCC)
    #
    #     # 触发验证
    #     register_page.submit_registration()
    #     time.sleep(1)
    #
    #     logger.info(f"📌 企业房东场景：执行空字段测试 [{scenario}]")
    #     check_register_error_messages(register_page, scenario, expected_errors)
    #
    # # ------------------------------
    # # 场景3：账户长度验证场景
    # # ------------------------------
    # username_length_cases = [
    #     # (场景标识, 房东类型, 注册信息, 预期错误提示)
    #     (
    #         "username_too_short",  # 用户名过短（1个字符）
    #         "个人",
    #         {
    #             "username": "a",  # 1个字符
    #             "password": "ValidP@ss123",
    #             "confirm_password": "ValidP@ss123",
    #             "phone_number": generate_random_phone_number(),
    #             "verify_code": "123456",
    #             "person_in_charge": "张三",
    #             "person_in_charge_ID": "110101199001011234",
    #             "person_in_charge_tel": "13987654321"
    #         },
    #         {"username": "账户长度必须在2到20个字符之间"}
    #     ),
    #     (
    #         "username_exactly_min",  # 用户名刚好2个字符（合法）
    #         "个人",
    #         {
    #             "username": "ab",  # 2个字符
    #             "password": "ValidP@ss123",
    #             "confirm_password": "ValidP@ss123",
    #             "phone_number": generate_random_phone_number(),
    #             "verify_code": "123456",
    #             "person_in_charge": "张三",
    #             "person_in_charge_ID": "110101199001011234",
    #             "person_in_charge_tel": "13987654321"
    #         },
    #         {}  # 无错误
    #     ),
    #     (
    #         "username_exactly_max",  # 用户名刚好20个字符（合法）
    #         "个人",
    #         {
    #             "username": "abcdefghijklmnopqrst",  # 20个字符
    #             "password": "ValidP@ss123",
    #             "confirm_password": "ValidP@ss123",
    #             "phone_number": "13812345678",
    #             "verify_code": "123456",
    #             "person_in_charge": "张三",
    #             "person_in_charge_ID": "110101199001011234",
    #             "person_in_charge_tel": "13987654321"
    #         },
    #         {}  # 无错误
    #     ),
    #     (
    #         "username_too_long",  # 用户名过长（21个字符）
    #         "企业",
    #         {
    #             "username": "abcdefghijklmnopqrstu",  # 21个字符
    #             "password": "ValidP@ss456",
    #             "confirm_password": "ValidP@ss456",
    #             "phone_number": "13787654321",
    #             "verify_code": "654321",
    #             "person_in_charge": "李四",
    #             "person_in_charge_ID": "310101198505056789",
    #             "person_in_charge_tel": "13612345678",
    #             "enterprise_name": "测试科技有限公司",
    #             "USCC": "91310000MA1FL7X123"
    #         },
    #         {"username": "账户长度必须在2到20个字符之间"}
    #     )
    # ]
    # username_length_ids = [case[0] for case in username_length_cases]
    #
    # @pytest.mark.parametrize(
    #     "scenario, fd_type, register_info, expected_errors",
    #     username_length_cases,
    #     ids=username_length_ids
    # )
    # def test_username_length_validation(
    #         self,
    #         page,
    #         base_url,
    #         scenario,
    #         fd_type,
    #         register_info,
    #         expected_errors
    # ):
    #     """测试账户长度必须在2到20个字符之间的验证逻辑"""
    #     register_page = RegisterPage(page)
    #     register_page.navigate(base_url)
    #     logger.info(
    #         f"测试场景: {scenario}, 用户名: {register_info['username']}, "
    #         f"长度: {len(register_info['username'])}"
    #     )
    #     logger.info(f"房东类型: {fd_type}")
    #
    #     # 选择房东类型
    #     register_page.select_fd_type(fd_type)
    #
    #     # 提取企业特有信息（如存在）
    #     enterprise_info = {}
    #     if fd_type == "企业":
    #         enterprise_info["enterprise_name"] = register_info.pop("enterprise_name")
    #         enterprise_info["USCC"] = register_info.pop("USCC")
    #
    #     # 填充基础注册信息
    #     register_page.fill_basic_info(**register_info)
    #
    #     # 填充企业信息（如为企业类型）
    #     if fd_type == "企业":
    #         register_page.fill_enterprise_info(**enterprise_info)
    #
    #     # 提交注册（触发验证）
    #     register_page.submit_registration()
    #     page.wait_for_timeout(1000)  # 等待验证结果
    #
    #     logger.info(f"📌 场景3：账户长度测试 [{scenario}]")
    #     check_register_alert_error_messages(register_page, scenario, expected_errors)
    #
    # # ------------------------------
    # # 场景4：密码格式验证（通用场景）
    # # ------------------------------
    # password_cases = [
    #     # 长度验证
    #     (
    #         "password_too_short",
    #         "Ab1!",
    #         "Ab1!",
    #         {"password": "长度在 8 到 20 个字符"}
    #     ),
    #     (
    #         "password_exactly_min_length",
    #         "Ab1!abcd",
    #         "Ab1!abcd",
    #         {}
    #     ),  # 刚好8位
    #     (
    #         "password_exactly_max_length",
    #         "Ab1!abcdefghijklmnopq",
    #         "Ab1!abcdefghijklmnopq",
    #         {}
    #     ),  # 刚好20位
    #     (
    #         "password_too_long",
    #         "Ab1!abcdefghijklmnopqr",
    #         "Ab1!abcdefghijklmnopqr",
    #         {"password": "长度在 8 到 20 个字符"}
    #     ),  # 21位
    #
    #     # 字符类型验证
    #     (
    #         "password_no_special",
    #         "Abcdefg123",
    #         "Abcdefg123",
    #         {"password": "需同时包含大小写英文、数字及特殊字符"}
    #     ),
    #     (
    #         "password_no_upper",
    #         "abcdefg1!",
    #         "abcdefg1!",
    #         {"password": "需同时包含大小写英文、数字及特殊字符"}
    #     ),
    #     (
    #         "password_no_lower",
    #         "ABCDEFG1!",
    #         "ABCDEFG1!",
    #         {"password": "需同时包含大小写英文、数字及特殊字符"}
    #     ),
    #     (
    #         "password_no_number",
    #         "Abcdefgh!",
    #         "Abcdefgh!",
    #         {"password": "需同时包含大小写英文、数字及特殊字符"}
    #     ),
    #
    #     # 一致性验证
    #     (
    #         "password_mismatch",
    #         "ValidP@ss123",
    #         "ValidP@ss456",
    #         {"confirm_password": "确认密码与密码不一致"}
    #     ),
    #     (
    #         "password_whitespace_mismatch",
    #         "ValidP@ss123 ",
    #         "ValidP@ss123",
    #         {"confirm_password": "确认密码与密码不一致"}
    #     ),  # 包含空格差异
    #
    #     # 特殊字符验证
    #     (
    #         "password_valid_special_chars",
    #         "Aa1!@#$%",
    #         "Aa1!@#$%",
    #         {}
    #     ),  # 多种特殊字符
    #     (
    #         "password_with_spaces",
    #         "Aa 1!bcde",
    #         "Aa 1!bcde",
    #         {}
    #     ),  # 包含空格
    #     (
    #         "password_chinese_chars",
    #         "密码Aa1!111",
    #         "密码Aa1!111",
    #         {"password": "需同时包含大小写英文、数字及特殊字符"}
    #     ),  # 包含中文字符
    #
    #     # 有效密码验证
    #     (
    #         "password_valid_min",
    #         "Aa1!abcd",
    #         "Aa1!abcd",
    #         {}
    #     ),  # 最小有效密码
    #     (
    #         "password_valid_medium",
    #         "Valid@1234",
    #         "Valid@1234",
    #         {}
    #     ),  # 中等长度有效密码
    #     (
    #         "password_valid_max",
    #         "ValidMaxP@ssw0rd123",
    #         "ValidMaxP@ssw0rd123",
    #         {}
    #     )  # 最大长度有效密码
    # ]
    # password_ids = [case[0] for case in password_cases]
    #
    # @pytest.mark.parametrize(
    #     "scenario, password, confirm_pwd, expected_errors",
    #     password_cases,
    #     ids=password_ids
    # )
    # def test_password_validation(
    #         self,
    #         page,
    #         base_url,
    #         scenario,
    #         password,
    #         confirm_pwd,
    #         expected_errors
    # ):
    #     """测试密码格式及一致性验证（适用于所有房东类型）"""
    #     register_page = RegisterPage(page)
    #     register_page.navigate(base_url)
    #
    #     # 测试个人房东场景
    #     register_page.select_fd_type("个人")
    #     register_page.fill_basic_info(
    #         username="test_password",
    #         phone_number="13800138000",
    #         password=password,
    #         confirm_password=confirm_pwd,
    #         verify_code="123456",
    #         person_in_charge="测试负责人",
    #         person_in_charge_ID="110101199001011234",
    #         person_in_charge_tel="13800138000",
    #         send_verification_code=False
    #     )
    #     register_page.submit_registration()
    #     time.sleep(1)
    #     logger.info(f"📌 密码验证场景：个人房东 [{scenario}]")
    #     check_register_error_messages(register_page, scenario, expected_errors)
    #
    #     # 测试企业房东场景
    #     register_page.select_fd_type("企业")
    #     register_page.fill_basic_info(
    #         username="test_password",
    #         phone_number="13800138000",
    #         verify_code="123456",
    #         password=password,
    #         confirm_password=confirm_pwd,
    #         person_in_charge="法定负责人",
    #         person_in_charge_ID="110101199001011234",
    #         person_in_charge_tel="13800138000",
    #         send_verification_code=False
    #     )
    #     register_page.fill_enterprise_info(
    #         enterprise_name="测试公司",
    #         USCC="91310000MA1FL7X123"
    #     )
    #
    #     register_page.submit_registration()
    #     time.sleep(1)
    #     logger.info(f"📌 密码验证场景：企业房东 [{scenario}]")
    #     check_register_error_messages(register_page, scenario, expected_errors)
    #
    # # ------------------------------
    # # 场景5：短信验证码验证（通用场景）
    # # ------------------------------
    # verify_code_cases = [
    #     ("code_wrong", "654321", {"verify_code": "验证码错误"}),
    #     ("code_expired", "987654", {"verify_code": "验证码错误"})
    # ]
    # verify_code_ids = [case[0] for case in verify_code_cases]
    #
    # @pytest.mark.parametrize(
    #     "scenario, code, expected_errors",
    #     verify_code_cases,
    #     ids=verify_code_ids
    # )
    # def test_verify_code_validation(
    #         self,
    #         page,
    #         base_url,
    #         scenario,
    #         code,
    #         expected_errors
    # ):
    #     """测试短信验证码验证（适用于所有房东类型）"""
    #     register_page = RegisterPage(page)
    #     register_page.navigate(base_url)
    #
    #     # 个人房东场景
    #     register_page.select_fd_type("个人")
    #     register_page.fill_basic_info(
    #         username="test_verify",
    #         phone_number="13800138000",
    #         verify_code=code,
    #         password="ValidP@ss123",
    #         confirm_password="ValidP@ss123",
    #         person_in_charge="测试负责人",
    #         person_in_charge_ID="110101199001011234",
    #         person_in_charge_tel="13800138000",
    #         send_verification_code=False
    #     )
    #
    #     register_page.submit_registration()
    #     time.sleep(2)  # 验证码验证需等待
    #     logger.info(f"📌 验证码场景：个人房东 [{scenario}]")
    #     check_register_alert_error_messages(register_page, scenario, expected_errors)
    #
    #     # 企业房东场景
    #     register_page.select_fd_type("企业")
    #     register_page.fill_basic_info(
    #         username="test_verify",
    #         phone_number="13800138000",
    #         verify_code=code,
    #         password="ValidP@ss123",
    #         confirm_password="ValidP@ss123",
    #         person_in_charge="法定负责人",
    #         person_in_charge_ID="110101199001011234",
    #         person_in_charge_tel="13800138000",
    #         send_verification_code=False
    #     )
    #     register_page.fill_enterprise_info(
    #         enterprise_name="测试公司",
    #         USCC="91310000MA1FL7X123"
    #     )
    #
    #     register_page.submit_registration()
    #     time.sleep(2)
    #     logger.info(f"📌 验证码场景：企业房东 [{scenario}]")
    #     check_register_alert_error_messages(register_page, scenario, expected_errors)
    #
    # # ------------------------------
    # # 场景6：类型切换验证
    # # ------------------------------
    # def test_fd_type_switch(self, page, base_url):
    #     """测试个人/企业类型切换时的字段显示逻辑"""
    #     register_page = RegisterPage(page)
    #     register_page.navigate(base_url)
    #
    #     # 初始默认类型验证（个人）
    #     # 验证个人选项被选中
    #     expect(register_page.fd).to_have_attribute("aria-checked", "true")
    #     expect(register_page.enterprise).not_to_have_attribute("aria-checked", "true")
    #     time.sleep(2)
    #
    #     # 切换到企业类型
    #     register_page.select_fd_type("企业")
    #     expect(register_page.fd).not_to_have_attribute("aria-checked", "true")
    #     expect(register_page.enterprise).to_have_attribute("aria-checked", "true")
    #     time.sleep(2)
    #
    #     # 验证企业特有字段存在
    #     expect(register_page.enterprise_name).to_be_visible()
    #     expect(register_page.USCC).to_be_visible()
    #
    #     logger.info("📌 类型切换测试：字段显示逻辑验证通过")
    #
    # # ------------------------------
    # # 场景7：电话号码有效性验证（覆盖所有电话字段）
    # # ------------------------------
    # phone_cases = [
    #     # 个人房东场景：联系电话（phone_number）
    #     (
    #         "personal_phone_number_invalid_short",
    #         "个人",
    #         "phone_number",
    #         "138001",
    #         "请输入有效的电话号码"
    #     ),
    #     (
    #         "personal_phone_number_invalid_letters",
    #         "个人",
    #         "phone_number",
    #         "138abc1234",
    #         "请输入有效的电话号码"
    #     ),  # 包含字母
    #     (
    #         "personal_phone_number_invalid_special",
    #         "个人",
    #         "phone_number",
    #         "138-0013-8000",
    #         "请输入有效的电话号码"
    #     ),  # 包含特殊字符
    #     (
    #         "personal_phone_number_invalid_mixed",
    #         "个人",
    #         "phone_number",
    #         "138a#12345",
    #         "请输入有效的电话号码"
    #     ),  # 混合字母和特殊字符
    #     (
    #         "personal_phone_number_valid",
    #         "个人",
    #         "phone_number",
    #         "13800138000",
    #         None
    #     ),
    #
    #     # 个人房东场景：负责人电话（person_in_charge_tel）
    #     (
    #         "personal_person_tel_invalid_short",
    #         "个人",
    #         "person_in_charge_tel",
    #         "139001",
    #         "请输入有效的电话号码"
    #     ),
    #     (
    #         "personal_person_tel_invalid_letters",
    #         "个人",
    #         "person_in_charge_tel",
    #         "139def4567",
    #         "请输入有效的电话号码"
    #     ),  # 包含字母
    #     (
    #         "personal_person_tel_invalid_special",
    #         "个人",
    #         "person_in_charge_tel",
    #         "139*0013*9000",
    #         "请输入有效的电话号码"
    #     ),  # 包含特殊字符
    #     (
    #         "personal_person_tel_invalid_mixed",
    #         "个人",
    #         "person_in_charge_tel",
    #         "139d$45678",
    #         "请输入有效的电话号码"
    #     ),  # 混合字母和特殊字符
    #     (
    #         "personal_person_tel_valid",
    #         "个人",
    #         "person_in_charge_tel",
    #         "13900139000",
    #         None
    #     ),
    #
    #     # 企业房东场景：联系电话（phone_number）
    #     (
    #         "enterprise_phone_number_invalid_short",
    #         "企业",
    #         "phone_number",
    #         "137001",
    #         "请输入有效的电话号码"
    #     ),
    #     (
    #         "enterprise_phone_number_invalid_letters",
    #         "企业",
    #         "phone_number",
    #         "137ghi7890",
    #         "请输入有效的电话号码"
    #     ),  # 包含字母
    #     (
    #         "enterprise_phone_number_invalid_special",
    #         "企业",
    #         "phone_number",
    #         "137_0013_7000",
    #         "请输入有效的电话号码"
    #     ),  # 包含特殊字符
    #     (
    #         "enterprise_phone_number_invalid_mixed",
    #         "企业",
    #         "phone_number",
    #         "137g%78901",
    #         "请输入有效的电话号码"
    #     ),  # 混合字母和特殊字符
    #     (
    #         "enterprise_phone_number_valid",
    #         "企业",
    #         "phone_number",
    #         "13700137000",
    #         None
    #     ),
    #
    #     # 企业房东场景：法定负责人电话（legal_person_in_charge_tel）
    #     (
    #         "enterprise_legal_tel_invalid_short",
    #         "企业",
    #         "legal_person_in_charge_tel",
    #         "136001",
    #         "请输入有效的电话号码"
    #     ),
    #     (
    #         "enterprise_legal_tel_invalid_letters",
    #         "企业",
    #         "legal_person_in_charge_tel",
    #         "136jkl0123",
    #         "请输入有效的电话号码"
    #     ),  # 包含字母
    #     (
    #         "enterprise_legal_tel_invalid_special",
    #         "企业",
    #         "legal_person_in_charge_tel",
    #         "136@0013@6000",
    #         "请输入有效的电话号码"
    #     ),  # 包含特殊字符
    #     (
    #         "enterprise_legal_tel_invalid_mixed",
    #         "企业",
    #         "legal_person_in_charge_tel",
    #         "136j#01234",
    #         "请输入有效的电话号码"
    #     ),  # 混合字母和特殊字符
    #     (
    #         "enterprise_legal_tel_valid",
    #         "企业",
    #         "legal_person_in_charge_tel",
    #         "13600136000",
    #         None
    #     ),
    # ]
    #
    # phone_ids = [case[0] for case in phone_cases]
    #
    # @pytest.mark.parametrize(
    #     "scenario, fd_type, phone_field, test_value, expected_error",
    #     phone_cases,
    #     ids=phone_ids
    # )
    # def test_phone_validation(
    #         self,
    #         page,
    #         base_url,
    #         scenario,
    #         fd_type,
    #         phone_field,
    #         test_value,
    #         expected_error
    # ):
    #     """测试所有电话字段（联系电话/负责人电话）的有效性验证"""
    #     register_page = RegisterPage(page)
    #     register_page.navigate(base_url)
    #     register_page.select_fd_type(fd_type)  # 选择房东类型
    #
    #     # 基础数据：所有字段默认有效，仅测试字段使用test_value
    #     basic_data = {
    #         "username": f"test_phone_{scenario}",
    #         "password": "ValidP@ss123",
    #         "confirm_password": "ValidP@ss123",
    #         "verify_code": "123456",
    #         "send_verification_code": False
    #     }
    #     personal_default = {
    #         "phone_number": "13800138000",  # 默认有效
    #         "person_in_charge": "个人负责人",
    #         "person_in_charge_ID": "110101199001011234",  # 有效身份证
    #         "person_in_charge_tel": "13900139000"  # 默认有效
    #     }
    #     basic_data.update(personal_default)
    #
    #     # 企业房东特有字段（默认有效）
    #     if fd_type == "企业":
    #         register_page.fill_enterprise_info(
    #             enterprise_name="测试企业",
    #             USCC="91310000MA1FL7X123"
    #         )
    #
    #     # 将测试值赋值给目标电话字段（覆盖默认值）
    #     if phone_field == "legal_person_in_charge_tel":
    #         basic_data["person_in_charge_tel"] = test_value
    #     else:
    #         basic_data[phone_field] = test_value
    #
    #     # 填充表单并提交
    #     logger.info(f"填充的表单数据: {basic_data}")
    #     register_page.fill_basic_info(**basic_data)
    #     register_page.submit_registration()
    #     time.sleep(1)
    #
    #     if expected_error:
    #         check_register_error_messages(register_page, {phone_field: expected_error})
    #
    # # ------------------------------
    # # 场景8：身份证号有效性验证（覆盖所有身份证字段）
    # # ------------------------------
    # id_card_cases = [
    #     # 个人房东：负责人身份证（person_in_charge_ID）
    #     (
    #         "personal_person_id_short",
    #         "个人",
    #         "person_in_charge_ID",
    #         "110101199001",
    #         "请输入有效的身份证号"
    #     ),
    #     (
    #         "personal_person_id_invalid",
    #         "个人",
    #         "person_in_charge_ID",
    #         "11010119900101123",
    #         "请输入有效的身份证号"
    #     ),
    #     (
    #         "personal_person_id_valid",
    #         "个人",
    #         "person_in_charge_ID",
    #         "110101199001011234",
    #         None
    #     ),
    #
    #     # 企业房东：法定负责人身份证（legal_person_in_charge_ID）
    #     (
    #         "enterprise_legal_id_short",
    #         "企业",
    #         "legal_person_in_charge_ID",
    #         "110101199001",
    #         "请输入有效的身份证号"
    #     ),
    #     (
    #         "enterprise_legal_id_invalid",
    #         "企业",
    #         "legal_person_in_charge_ID",
    #         "11010119900101123",
    #         "请输入有效的身份证号"
    #     ),
    #     (
    #         "enterprise_legal_id_valid",
    #         "企业",
    #         "legal_person_in_charge_ID",
    #         "110101199001011234",
    #         None
    #     ),
    # ]
    # id_card_ids = [case[0] for case in id_card_cases]
    #
    # @pytest.mark.parametrize(
    #     "scenario, fd_type, id_field, test_value, expected_error",
    #     id_card_cases,
    #     ids=id_card_ids
    # )
    # def test_id_card_validation(
    #         self,
    #         page,
    #         base_url,
    #         scenario,
    #         fd_type,
    #         id_field,
    #         test_value,
    #         expected_error
    # ):
    #     """测试所有身份证字段（个人/企业负责人）的有效性验证"""
    #     register_page = RegisterPage(page)
    #     register_page.navigate(base_url)
    #     register_page.select_fd_type(fd_type)
    #
    #     # 基础数据（默认有效，避免其他字段干扰）
    #     basic_data = {
    #         "username": f"test_id_{scenario}",
    #         "password": "ValidP@ss123",
    #         "confirm_password": "ValidP@ss123",
    #         "verify_code": "123456",
    #         "send_verification_code": False
    #     }
    #
    #     personal_default = {
    #         "phone_number": "13800138000",
    #         "person_in_charge": "个人负责人",
    #         "person_in_charge_ID": "110101199001011234",  # 默认有效
    #         "person_in_charge_tel": "13900139000"
    #     }
    #     basic_data.update(personal_default)
    #
    #     # 企业房东默认数据
    #     if fd_type == "企业":
    #         register_page.fill_enterprise_info(
    #             enterprise_name="测试企业",
    #             USCC="91310000MA1FL7X123"
    #         )
    #
    #     # 覆盖目标身份证字段为测试值
    #     if id_field == "legal_person_in_charge_ID":
    #         basic_data["person_in_charge_ID"] = test_value
    #     else:
    #         basic_data[id_field] = test_value
    #
    #     # 填充并提交
    #     register_page.fill_basic_info(**basic_data)
    #     register_page.submit_registration()
    #     time.sleep(1)
    #
    #     # 验证结果
    #     logger.info(f"📌 身份证验证：{scenario}")
    #     if expected_error:
    #         check_register_error_messages(register_page, {id_field: expected_error})
    #
    # # ------------------------------
    # # 场景9：验证码按钮行为验证
    # # ------------------------------
    # verify_code_button_cases = [
    #     # (场景标识, 房东类型, 手机号, 预期错误提示, 预期按钮状态变化)
    #     (
    #         "valid_phone_personal",
    #         "个人",
    #         "13800138000",
    #         None,
    #         "countdown"
    #     ),  # 标记为倒计时状态
    # ]
    # verify_code_button_ids = [case[0] for case in verify_code_button_cases]
    #
    # @pytest.mark.parametrize(
    #     "scenario, fd_type, phone_number, expected_error, expected_button_text",
    #     verify_code_button_cases,
    #     ids=verify_code_button_ids
    # )
    # def test_verify_code_button_behavior(
    #         self,
    #         page,
    #         base_url,
    #         scenario,
    #         fd_type,
    #         phone_number,
    #         expected_error,
    #         expected_button_text
    # ):
    #     """测试验证码按钮点击行为（空手机号、无效手机号、有效手机号场景）"""
    #     register_page = RegisterPage(page)
    #     register_page.navigate(base_url)
    #     register_page.select_fd_type(fd_type)
    #
    #     register_page.phone.fill(phone_number)
    #
    #     # 点击获取验证码按钮
    #     initial_button_text = register_page.get_verify_code_button_text()
    #     register_page.verify_code_button.click()
    #     time.sleep(1)
    #
    #     # 验证错误提示
    #     if expected_error:
    #         logger.info(f"📌 验证码按钮场景：{scenario} - 验证错误提示")
    #         check_register_error_messages(register_page, {"phone_number": expected_error})
    #         # 验证按钮状态未变
    #         assert register_page.get_verify_code_button_text() == initial_button_text
    #         assert register_page.is_verify_code_button_enabled()
    #     else:
    #         # 验证倒计时状态 - 匹配实际HTML结构
    #         logger.info(f"📌 验证码按钮场景：{scenario} - 验证码发送成功")
    #         check_register_alert_error_messages(register_page, {"verify_code": "验证码发送成功"})
    #         logger.info(f"📌 验证码按钮场景：{scenario} - 验证倒计时")
    #
    #         # 验证按钮处于禁用状态
    #         assert not register_page.is_verify_code_button_enabled()
    #         assert "is-disabled" in register_page.get_verify_code_button_class()
    #         assert register_page.get_verify_code_button_attribute("disabled") == "disabled"
    #
    #         # 验证倒计时文本格式 (获取验证码(XXs))
    #         countdown_text = register_page.get_verify_code_button_text()
    #         assert "获取验证码" in countdown_text
    #         assert re.match(r"获取验证码\(\d+s\)", countdown_text)
    #
    #         # 提取倒计时数字并验证在合理范围内
    #         countdown_seconds = int(re.search(r"\d+", countdown_text).group())
    #         assert 0 < countdown_seconds <= 60
    #
    #         # 等待倒计时结束
    #         time.sleep(countdown_seconds + 2)  # 等待剩余时间+缓冲时间
    #
    #         # 验证按钮恢复正常状态
    #         logger.info(f"📌 验证码按钮场景：{scenario} - 验证倒计时结束后状态")
    #         assert register_page.get_verify_code_button_text() == "获取验证码"
    #         assert register_page.is_verify_code_button_enabled()
    #         assert "is-disabled" not in register_page.get_verify_code_button_class()
    #         assert register_page.get_verify_code_button_attribute("disabled") is None
    #
    # # ------------------------------
    # # 场景10：注册成功场景（个人/企业房东）
    # # ------------------------------
    # register_success_cases = [
    #     # (场景标识, 房东类型, 注册信息)
    #     (
    #         "personal_register_success",
    #         "个人",
    #         {
    #             "username": "personal_success_123",
    #             "password": "ValidP@ss123",
    #             "confirm_password": "ValidP@ss123",
    #             "phone_number": "13812345678",
    #             "verify_code": "123456",  # 假设此验证码有效
    #             "person_in_charge": "张三",
    #             "person_in_charge_ID": "110101199001011234",  # 有效身份证
    #             "person_in_charge_tel": "13987654321"
    #         }
    #     ),
    #     (
    #         "enterprise_register_success",
    #         "企业",
    #         {
    #             "username": "ent_success_456",
    #             "password": "ValidP@ss456",
    #             "confirm_password": "ValidP@ss456",
    #             "phone_number": "13787654321",
    #             "verify_code": "654321",  # 假设此验证码有效
    #             "person_in_charge": "李四",
    #             "person_in_charge_ID": "310101198505056789",  # 有效身份证
    #             "person_in_charge_tel": "13612345678",
    #             "enterprise_name": "测试科技有限公司",
    #             "USCC": "91310000MA1FL7X123"  # 有效统一社会信用代码
    #         }
    #     )
    # ]
    # register_success_ids = [case[0] for case in register_success_cases]
    #
    # @pytest.mark.parametrize(
    #     "scenario, fd_type, register_info",
    #     register_success_cases,
    #     ids=register_success_ids
    # )
    # def test_register_success_and_login(
    #         self,
    #         page,
    #         base_url,
    #         scenario,
    #         fd_type,
    #         register_info
    # ):
    #     """测试个人/企业房东注册成功后，使用注册信息登录成功"""
    #     # 1. 执行注册流程
    #     register_page = RegisterPage(page)
    #     register_page.navigate(base_url)
    #     logger.info(f"注册信息: {register_info}")
    #     logger.info(f"房东类型: {fd_type}")
    #     register_page.select_fd_type(fd_type)
    #
    #     # 提取企业特有信息（如存在）
    #     enterprise_info = {}
    #     if fd_type == "企业":
    #         enterprise_info["enterprise_name"] = register_info.pop("enterprise_name")
    #         enterprise_info["USCC"] = register_info.pop("USCC")
    #
    #     # 填充基础注册信息
    #     register_page.fill_basic_info(**register_info)
    #
    #     # 填充企业信息（如为企业类型）
    #     if fd_type == "企业":
    #         register_page.fill_enterprise_info(**enterprise_info)
    #
    #     # 提交注册
    #     register_page.submit_registration()
    #     page.wait_for_timeout(2000)  # 等待页面响应
    #
    #     # 2. 验证注册成功并跳转至登录页
    #     # 验证成功提示对话框
    #     username = register_info.get("username")
    #     register_page.get_register_success_dialog(f"恭喜你，您的账号 {username} 注册成功！")
    #
    #     # 点击按钮并验证跳转至登录页
    #     if fd_type == "个人":
    #         register_page.click_sure_button_and_verify_redirect(base_url)  # 默认跳转/login
    #     elif fd_type == "企业":
    #         register_page.close_dialog_and_verify_redirect(base_url)
    #
    #     # 3. 使用注册信息执行登录操作
    #     try:
    #         login_page = LoginPage(page)
    #
    #         # 填充登录信息（使用注册时的用户名和密码）
    #         login_page.fill_credentials(
    #             login_username=register_info["username"],
    #             login_password=register_info["password"]
    #         )
    #
    #         # 提交登录
    #         login_page.click_login_button()
    #         # 拼接完整的预期 URL（base_url + 路径）
    #         expected_url = f"{base_url}/fangdonghome"
    #         expected_title = "网约房智慧安全监管平台"
    #         page.wait_for_url(expected_url)
    #         logger.info(f" 执行登录成功测试场景：{scenario}")
    #         # 验证跳转正确
    #         check_page_title(page, expected_title)
    #
    #     except AssertionError as e:
    #         logger.error(f"❌ 注册后登录验证失败 [{scenario}]: {str(e)}")
    #         raise
    #
    # ------------------------------
    # 场景11：已存在用户名的验证场景
    # ------------------------------
    existing_username_cases = [
        # (场景标识, 房东类型, 注册信息, 预期错误提示)
        (
            "personal_existing_username",  # 个人房东使用已存在用户名
            "个人",
            {
                "username": "fenghuang_456",  # 假设该用户名已存在
                "password": "Aa123123!",
                "confirm_password": "Aa123123!",
                "phone_number": "13812345777",
                "verify_code": "123456",
                "person_in_charge": "张三",
                "person_in_charge_ID": "110101199001011234",
                "person_in_charge_tel": "13987654377"
            },
            {"username": "用户名已存在"}
        ),
        (
            "enterprise_existing_username",  # 企业房东使用已存在用户名
            "企业",
            {
                "username": "existing_user_123",  # 与个人场景使用相同的已存在用户名
                "password": "ValidP@ss456",
                "confirm_password": "ValidP@ss456",
                "phone_number": "13787654321",
                "verify_code": "654321",
                "person_in_charge": "李四",
                "person_in_charge_ID": "310101198505056789",
                "person_in_charge_tel": "13612345678",
                "enterprise_name": "测试科技有限公司",
                "USCC": "91310000MA1FL7X123"
            },
            {"username": "用户名已存在"}
        )
    ]
    existing_username_ids = [case[0] for case in existing_username_cases]

    @pytest.mark.parametrize(
        "scenario, fd_type, register_info, expected_errors",
        existing_username_cases,
        ids=existing_username_ids
    )
    def test_existing_username_validation(
            self,
            page,
            base_url,
            scenario,
            fd_type,
            register_info,
            expected_errors
    ):
        """测试使用已存在的用户名进行注册时的验证逻辑"""
        register_page = RegisterPage(page)
        register_page.navigate(base_url)
        logger.info(
            f"测试场景: {scenario}, 已存在的用户名: {register_info['username']}"
        )
        logger.info(f"房东类型: {fd_type}")

        # 选择房东类型
        register_page.select_fd_type(fd_type)

        # 提取企业特有信息（如存在）
        enterprise_info = {}
        if fd_type == "企业":
            enterprise_info["enterprise_name"] = register_info.pop("enterprise_name")
            enterprise_info["USCC"] = register_info.pop("USCC")

        # 填充基础注册信息
        register_page.fill_basic_info(**register_info)

        # 填充企业信息（如为企业类型）
        if fd_type == "企业":
            register_page.fill_enterprise_info(**enterprise_info)

        # 提交注册（触发验证）
        register_page.submit_registration()
        page.wait_for_timeout(2000)  # 等待后端验证结果（网络请求需要更长时间）

        # 验证错误提示
        check_register_alert_error_messages(register_page, scenario, expected_errors)