from tests.utils.page_utils import *
from  tests.utils.validator import *
from playwright.sync_api import Page

class RegisterPage:
    def __init__(self, page: Page):
        self.page = page

        prefix = "法定"
        # 页面元素定位
        self.username = get_label_corresponding_input(self.page,  "用户名")
        self.password = get_label_corresponding_input(self.page,  "密码")
        self.password_conform= get_label_corresponding_input(self.page,  "确认密码")
        self.phone = get_label_corresponding_input(self.page,  "联系电话")
        self.verify_code = get_label_corresponding_input(self.page,  "短信验证码")
        self.verify_code_button = self.page.get_by_role("button", name="获取验证码")
        self.fd = self.page.locator(f'label:has-text("个人")')
        self.enterprise = self.page.locator(f'label:has-text("企业")')
        self.person_in_charge = get_label_corresponding_input(self.page,  "负责人姓名")
        self.person_in_charge_ID= get_label_corresponding_input(self.page,  "负责人身份证号")
        self.person_in_charge_tel = get_label_corresponding_input(self.page,  "负责人联系电话")

        self.legal_person_in_charge = get_label_corresponding_input(self.page, "法定负责人姓名")
        self.legal_person_in_charge_ID= get_label_corresponding_input(self.page, "法定负责人身份证号")
        self.legal_person_in_charge_tel = get_label_corresponding_input(self.page, "法定负责人联系电话")

        self.enterprise_name = get_label_corresponding_input(self.page,  "企业名称")
        self.USCC = get_label_corresponding_input(self.page, "统一社会信用代码")
        self.register_button = self.page.get_by_text("注 册",exact=True)
        self.cancel_button = self.page.get_by_role("button", name="取消")
        self.error_messages = self.page.locator('[class*="error"]')

    def navigate(self, base_url):
        try:
            self.page.goto(f"{base_url}/login")
            self.page.get_by_text("房东注册").click()
        except Exception as e:
            self.page.screenshot(path=f"{base_url}_navigate_error.png")
            raise e

    def select_fd_type(self, fd_type = "个人"):
        """选择房东类型（个人或企业）"""
        try:
            if fd_type == "个人":
                self.fd.click()
            elif fd_type == "企业":
                self.enterprise.click()
            else:
                raise ValueError(f"Invalid fd_type: {fd_type}. Allowed values are '个人' or '企业'.")
        except Exception as e:
            self.page.screenshot(path=f"select_fd_type_error.png")
            raise e

    def fill_basic_info(self, username: str = "", password: str = "", phone_number: str = "", fd_type: str = "个人",
                        person_in_charge: str = "", person_in_charge_ID: str = "", person_in_charge_tel: str = "", password_conform: str | None = None):
        """填写基础注册信息"""
        try:
            self.username.fill(username)
            self.password.fill(password)
            if password_conform is not None:
                self.password_conform.fill(password_conform)
            else:
                self.password_conform.fill(password)
            self.phone.fill(phone_number)
            # self.send_verification_code(phone_number)
            if fd_type == "个人":
                self.person_in_charge.fill(person_in_charge)
                self.person_in_charge_ID.fill(person_in_charge_ID)
                self.person_in_charge_tel.fill(person_in_charge_tel)

            elif fd_type == "企业":
                self.legal_person_in_charge.fill(person_in_charge)
                self.legal_person_in_charge_ID.fill(person_in_charge_ID)
                self.legal_person_in_charge_tel.fill(person_in_charge_tel)
            else:
                raise ValueError(f"Invalid fd_type: {fd_type}. Allowed values are '个人' or '企业'.")
        except Exception as e:
            self.page.screenshot(path=f"{fd_type}_fill_basic_info_error.png")
            raise e

    def fill_enterprise_info(self, enterprise_name: str, USCC: str):
        try:
            scroll_to_bottom(self.page)
            self.enterprise_name.fill(enterprise_name)
            self.USCC.fill(USCC)
        except Exception as e:
            self.page.screenshot(path=f"fill_enterprise_info_error.png")
            raise e

    # def send_verification_code(self, phone_number: str):
    #     """发送短信验证码（需处理异步操作）"""
    #     try:
    #         self.verify_code_button.click()
    #         verify_code = extract_verification_code_live("192.168.40.61", "root", "dell_123456", "22","/opt/tomcat8.5.84-wyf-fd-3333/logs/catalina.out",
    #                                phone_number)
    #         self.verify_code.fill(verify_code)
    #     except Exception as e:
    #         self.page.screenshot(path=f"send_verification_code_error.png")
    #         raise e

    def submit_registration(self):
        """提交注册表单"""
        try:
            scroll_to_bottom(self.page)
            self.register_button.click()
        except Exception as e:
            self.page.screenshot(path=f"submit_registration_error.png")
            raise e

    def get_success_text(self, expected_text):
        try:
            wait_for_dialog(self.page, expected_text)
        except Exception as e:
            self.page.screenshot(path=f"get_success_text_error.png")
            raise e

    def get_error_tip(self, target_label, expected_text):
        try:
            get_label_corresponding_error_tip(self.page, target_label, expected_text)
        except Exception as e:
            self.page.screenshot(path=f"get_success_text_error.png")
            raise e

    # def get_element_corresponding_error(self, element: Locator, message: str) -> bool:
    #     """检查指定元素是否显示对应的错误提示"""
    #     error_locator = '../following-sibling::div[contains(@class, "el-form-item__error")]'
    #     return get_placeholder_corresponding_error_tip(self.page, element, error_locator, message)

    def username_error(self, message: str) -> bool:
        """检查账号输入框是否显示指定的错误提示"""
        return get_placeholder_corresponding_error_tip(self.page, self.username, '../following-sibling::div[contains(@class, "el-form-item__error")]', message)

    def password_error(self, message: str) -> bool:
        """检查密码输入框是否显示指定的错误提示"""
        return get_placeholder_corresponding_error_tip(self.page, self.password, '../following-sibling::div[contains(@class, "el-form-item__error")]', message)

    def password_conform_error(self, message: str) -> bool:
        """检查确认密码输入框是否显示指定的错误提示"""
        return get_placeholder_corresponding_error_tip(self.page, self.password_conform, '../following-sibling::div[contains(@class, "el-form-item__error")]', message)

    def phone_error(self, message: str) -> bool:
        """检查联系电话输入框是否显示指定的错误提示"""
        return get_placeholder_corresponding_error_tip(self.page, self.phone, '../following-sibling::div[contains(@class, "el-form-item__error")]', message)

    def verify_code_error(self, message: str) -> bool:
        """检查短信验证码输入框是否显示指定的错误提示"""
        return get_placeholder_corresponding_error_tip(self.page, self.verify_code, '../following-sibling::div[contains(@class, "el-form-item__error")]', message)

    def person_in_charge_error(self, message: str) -> bool:
        """检查负责人姓名输入框是否显示指定的错误提示"""
        return get_placeholder_corresponding_error_tip(self.page, self.person_in_charge, '../following-sibling::div[contains(@class, "el-form-item__error")]', message)

    def person_in_charge_ID_error(self, message: str) -> bool:
        """检查负责人身份证号输入框是否显示指定的错误提示"""
        return get_placeholder_corresponding_error_tip(self.page, self.person_in_charge_ID, '../following-sibling::div[contains(@class, "el-form-item__error")]', message)

    def person_in_charge_tel_error(self, message: str) -> bool:
        """检查负责人联系电话输入框是否显示指定的错误提示"""
        return get_placeholder_corresponding_error_tip(self.page, self.person_in_charge_tel, '../following-sibling::div[contains(@class, "el-form-item__error")]', message)

    def legal_person_in_charge_error(self, message: str) -> bool:
        """检查法定负责人姓名输入框是否显示指定的错误提示"""
        return get_placeholder_corresponding_error_tip(self.page, self.legal_person_in_charge, '../following-sibling::div[contains(@class, "el-form-item__error")]', message)

    def legal_person_in_charge_ID_error(self, message: str) -> bool:
        """检查法定负责人身份证号输入框是否显示指定的错误提示"""
        return get_placeholder_corresponding_error_tip(self.page, self.legal_person_in_charge_ID, '../following-sibling::div[contains(@class, "el-form-item__error")]', message)

    def legal_person_in_charge_tel_error(self, message: str) -> bool:
        """检查法定负责人联系电话输入框是否显示指定的错误提示"""
        return get_placeholder_corresponding_error_tip(self.page, self.legal_person_in_charge_tel, '../following-sibling::div[contains(@class, "el-form-item__error")]', message)

    def enterprise_name_error(self, message: str) -> bool:
        """检查企业名称输入框是否显示指定的错误提示"""
        return get_placeholder_corresponding_error_tip(self.page, self.enterprise_name, '../following-sibling::div[contains(@class, "el-form-item__error")]', message)

    def USCC_error(self, message: str) -> bool:
        """检查统一社会信用代码输入框是否显示指定的错误提示"""
        return get_placeholder_corresponding_error_tip(self.page, self.USCC, '../following-sibling::div[contains(@class, "el-form-item__error")]', message)

    def confirm_password_error(self, message: str) -> bool:
        """检查统一社会信用代码输入框是否显示指定的错误提示"""
        return get_placeholder_corresponding_error_tip(self.page, self.password_conform, '../following-sibling::div[contains(@class, "el-form-item__error")]', message)