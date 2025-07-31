# base page operations
import time
from typing import Union, List
from faker import Faker
from typing import Optional, List
from playwright.async_api import Page, Locator
from conf.logging_config import logger
from tests.conftest import base_url
from tests.utils.validator import *


def find_file_input(label):
    """
    查找标签对应的文件输入框

    Args:
        label: 标签元素

    Returns:
        ElementHandle: 文件输入框元素，如果未找到则返回None
    """
    try:
        return label.query_selector('xpath=following-sibling::div').query_selector(
            'xpath=//input[@type="file"]')
    except AttributeError:
        return None

def scroll_to_bottom(page: Page) -> None:
    """
    滚动到页面底部

    :param page: Playwright的Page对象
    """
    try:
        # 按下End键，尝试快速滚动到页面底部
        page.keyboard.press('End')
        # 等待500毫秒，确保页面滚动完成
        page.wait_for_timeout(500)

        # 循环5次，每次按下PageDown键，进一步微调滚动位置
        for _ in range(5):
            page.keyboard.press('PageDown')
            page.wait_for_timeout(300)
    except Exception as e:
        # 若滚动过程中出现异常，记录错误日志
        logger.error(f"滚动到页面底部时出错: {e}")

def scroll_to_keywords_view(page: Page, keywords) -> None:
    """
    滚动到包含指定关键字的元素可见区域

    :param page: Playwright的Page对象
    :param keywords: 要查找的关键字
    """
    try:
        # 定位包含指定关键字的元素（模糊匹配）
        element = page.locator(f':text-matches(".*{keywords}.*")')
        # 滚动到元素位置，确保元素可见
        element.scroll_into_view_if_needed()
    except Exception as e:
        # 若滚动过程中出现异常，记录错误日志
        logger.error(f"滚动到关键字 {keywords} 视图时出错: {e}")

def locate_elements_by_step_strategy(target_label: Locator, xpath: str) -> Optional[Locator]:
    """
    使用分步策略定位元素

    :param target_label: 标签元素的Locator
    :param xpath: 自定义XPath表达式
    :return: 定位到的元素Locator或None
    """
    # 尝试分步定位策略
    steps = xpath.split('//', 1)  # 拆分为两部分

    if len(steps) > 1:
        first_step, remaining_steps = steps
        # 第一步：定位到中间元素
        middle_locator = target_label.locator(f'xpath={first_step}')
        # 检查第一步是否成功
        if middle_locator.count() > 0:
            logger.info(f"第一步定位成功: {first_step}")
            # 第二步：在中间元素基础上继续定位
            final_locator = middle_locator.locator(f'xpath=//{remaining_steps}')
            try:
                # 返回所有定位到的元素
                return final_locator
            except TimeoutError:
                pass  # 继续尝试其他策略

    # 原始的整体定位策略作为后备
    # logger.info(f"尝试整体定位: {xpath}")
    relative_locator = target_label.locator(f'xpath={xpath}')
    try:
        # 返回所有定位到的元素
        return relative_locator.all()
    except TimeoutError:
        # 若定位超时，抛出异常
        raise ValueError(f"对应的元素，XPath: {xpath}")

def locate_element_by_step_strategy(target_label: Locator, xpath: str) -> Locator:
    """
    使用分步策略定位单个元素（确保返回非空Locator）

    :param target_label: 标签元素的Locator
    :param xpath: 自定义XPath表达式
    :return: 定位到的单个元素Locator
    :raises ValueError: 当元素无法定位时抛出异常
    """
    # 尝试分步定位策略
    steps = xpath.split('//', 1)  # 拆分为两部分

    if len(steps) > 1:
        first_step, remaining_steps = steps
        # 第一步：定位到中间元素
        middle_locator = target_label.locator(f'xpath={first_step}')
        # 检查第一步是否成功
        if middle_locator.count() > 0:
            logger.info(f"第一步定位成功: {first_step}")
            # 第二步：在中间元素基础上继续定位
            final_locator = middle_locator.locator(f'xpath=//{remaining_steps}')
            # 使用nth(0)确保返回Locator对象，元素不存在时会触发超时
            return final_locator.nth(0)

    # 原始的整体定位策略作为后备
    # logger.info(f"尝试整体定位: {xpath}")
    relative_locator = target_label.locator(f'xpath={xpath}')
    # 使用nth(0)确保返回Locator对象，元素不存在时会触发超时
    element = relative_locator.nth(0)

    # 显式检查元素是否存在（超时处理）
    try:
        return element
    except TimeoutError:
        raise ValueError(f"无法定位元素，XPath: {xpath}")

def upload_file(page: Page, file_path: str) -> None:
    """
    上传文件

    :param page: Playwright的Page对象
    :param file_path: 要上传的文件路径
    """
    try:
        # 先滚动到页面底部
        scroll_to_bottom(page)
        # 查询页面上的文件输入框
        upload_input = page.query_selector('input[type="file"]')
        if upload_input is None:
            # 若未找到文件输入框，抛出异常
            raise ValueError("未找到文件输入框")
        # 设置要上传的文件路径
        upload_input.set_input_files(file_path)
    except Exception as e:
        # 若上传文件过程中出现异常，记录错误日志
        logger.error(f"上传文件 {file_path} 时出错: {e}")

def get_label_corresponding_content(page: Page, element, label_text, value_locator_xpath) -> str:
    """
    获取指定标签对应的内容，例如获取用户名密码的值

    :param page: Playwright的Page对象
    :param element: 定位的基础元素
    :param label_text: 标签文本
    :param value_locator_xpath: 用于定位值的XPath表达式
    :return: 标签对应的内容
    """
    try:
        # 定位指定标签元素
        target_label = element.locator(f'label:has-text("{label_text}")')
        # 定位标签对应的内容元素
        target_value = target_label.locator(f'xpath={value_locator_xpath}')
        # 获取内容元素的文本内容
        return target_value.text_content()
    except Exception as e:
        # 若获取内容过程中出现异常，记录错误日志并抛出异常
        logger.error(f"获取标签 {label_text} 对应的内容时出错: {e}")
        raise

def get_label_corresponding_error_tip(page: Page, label_text: str, expected_message):
    """
    获取指定标签对应的错误提示信息，并验证是否符合预期

    :param page: Playwright的Page对象
    :param label_text: 标签文本
    :param expected_message: 预期的错误提示信息
    """
    try:
        # 定位指定标签元素
        target_label = page.get_by_text(label_text, exact=True)
        # 定位标签对应的错误提示元素
        target_element = target_label.locator('.el-form-item__error')
        # 获取错误提示元素的文本内容并去除首尾空白
        error_text = target_element.text_content().strip()
        # 验证错误提示信息是否符合预期
        assert error_text == expected_message, f"错误提示信息不符，预期: {expected_message}，实际: {error_text}"
    except AssertionError as ae:
        # 若验证失败，记录错误日志并抛出异常
        logger.error(f"验证标签 {label_text} 的错误提示信息时出错: {ae}")
        raise
    except Exception as e:
        # 若获取错误提示信息过程中出现其他异常，记录错误日志并抛出异常
        logger.error(f"获取标签 {label_text} 对应的错误提示信息时出错: {e}")
        raise

def get_label_corresponding_input(page: Page, label_text) -> Locator:
    """
    获取指定标签对应的输入框

    :param page: Playwright的Page对象
    :param label_text: 标签文本
    :return: 定位到的输入框Locator对象
    """
    try:
        # 定位指定标签元素
        target_label = page.get_by_text(label_text, exact=True)
        # 定位标签对应的输入框元素
        target_element = target_label.locator('xpath=following-sibling::div//input')
        return target_element
    except Exception as e:
        # 若获取输入框过程中出现异常，记录错误日志并抛出异常
        logger.error(f"获取标签 {label_text} 对应的输入框时出错: {e}")
        raise


def get_label_corresponding_element(page: Page, label_text: str, xpath: str) -> Locator:
    """
    获取与标签文本对应的表单元素（分步定位策略）

    :param page: Playwright的Page对象
    :param label_text: 标签文本内容
    :param xpath: 自定义XPath表达式，用于定位目标元素
    :return: 定位到的表单元素Locator，若未找到则返回None
    :raises ValueError: 未提供自定义XPath表达式
    """
    if not xpath:
        # 若未提供XPath表达式，抛出异常
        raise ValueError("必须提供自定义XPath表达式")
    try:
        # 定位标签元素
        target_label = page.get_by_text(label_text, exact=True)
        # 检查标签是否可见
        if not target_label.is_visible():
            # 若标签不可见，抛出异常
            raise ValueError(f"未找到标签文本: '{label_text}'")

        # 尝试分步定位策略
        steps = xpath.split('//', 1)  # 拆分为两部分

        if len(steps) > 1:
            first_step, remaining_steps = steps
            # 第一步：定位到中间元素
            middle_locator = target_label.locator(f'xpath={first_step}')
            # 检查第一步是否成功
            if middle_locator.count() > 0 and middle_locator.is_visible():
                logger.info(f"第一步定位成功: {first_step}")
                # 第二步：在中间元素基础上继续定位
                final_locator = middle_locator.locator(f'xpath=//{remaining_steps}')

                # 新增：检查最终元素是否存在
                if final_locator.count() == 0:
                    logger.info(f"第二步定位未找到元素: //{remaining_steps}")
                    return None

                return final_locator

        # 原始的整体定位策略作为后备
        # logger.info(f"尝试整体定位: {xpath}")
        relative_locator = target_label.locator(f'xpath={xpath}')

        # 新增：检查是否找到元素
        if relative_locator.count() == 0:
            return None

        return relative_locator
    except TimeoutError:
        # 若定位超时，返回None而非抛出异常
        logger.warning(f"定位超时，未找到与标签 '{label_text}' 对应的可见元素，XPath: {xpath}")
        return None
    except Exception as e:
        # 若出现其他异常，记录错误日志并抛出异常
        logger.error(f"获取标签 {label_text} 对应的元素时出错: {e}")
        raise

def get_label_corresponding_elements(page: Page, label_text: str, xpath: str, timeout: int = 3000) -> List[Locator]:
    """
    获取与标签文本对应的所有表单元素（不强制要求元素可见）

    :param page: Playwright的Page对象
    :param label_text: 标签文本内容
    :param xpath: 自定义XPath表达式，用于定位目标元素
    :param timeout: 等待元素存在的超时时间（毫秒），默认为3000ms
    :return: 定位到的所有元素Locator列表
    :raises ValueError: 未找到匹配的元素
    """
    if not xpath:
        # 若未提供XPath表达式，抛出异常
        raise ValueError("必须提供自定义XPath表达式")
    try:
        # 定位标签元素
        target_label = page.get_by_text(label_text, exact=True)
        # 等待标签元素出现
        target_label.wait_for(timeout=timeout)
    except TimeoutError:
        # 若未找到精确匹配的标签元素，尝试非精确匹配作为后备
        target_label = page.get_by_text(label_text)
        try:
            # 等待非精确匹配的标签元素出现
            target_label.wait_for(timeout=timeout)
        except TimeoutError:
            # 若仍未找到标签元素，抛出异常
            raise ValueError(f"未找到标签文本: '{label_text}'")

    # 尝试分步定位策略
    steps = xpath.split('//', 1)  # 拆分为两部分

    if len(steps) > 1:
        first_step, remaining_steps = steps
        # 第一步：定位到中间元素
        middle_locator = target_label.locator(f'xpath={first_step}')
        # 检查第一步是否成功
        if middle_locator.count() > 0:
            logger.info(f"第一步定位成功: {first_step}")
            # 第二步：在中间元素基础上继续定位
            final_locator = middle_locator.locator(f'xpath=//{remaining_steps}')
            try:
                # 返回所有定位到的元素
                return final_locator.all()
            except TimeoutError:
                pass  # 继续尝试其他策略

    # 原始的整体定位策略作为后备
    # logger.info(f"尝试整体定位: {xpath}")
    relative_locator = target_label.locator(f'xpath={xpath}')
    try:
        # 返回所有定位到的元素
        return relative_locator.all()
    except TimeoutError:
        # 若定位超时，抛出异常
        raise ValueError(f"未找到与标签 '{label_text}' 对应的元素，XPath: {xpath}")

def get_element_corresponding_error_tip(target_element: Locator, xpath: str, expected_message: str) -> bool:
    """
    获取指定占位符对应的错误提示信息，并验证是否符合预期

    :param page: Playwright的Page对象
    :param target_element: 目标元素
    :param xpath: 自定义XPath表达式，用于定位错误提示元素
    :param expected_message: 预期的错误提示信息
    :param timeout: 等待元素出现的超时时间（毫秒），默认为3000ms
    """
    if not xpath:
        raise ValueError("必须提供自定义XPath表达式")

    try:
        # 定位包含指定占位符文本的输入元素
        # target_input = page.get_by_role("textbox", name=placeholder_text)

        # 使用分步定位策略查找错误提示元素
        final_locator = locate_element_by_step_strategy(target_element, xpath)

        if final_locator:
            error_element = final_locator
        else:
            # 后备策略：使用相对定位
            logger.info(f"分步定位失败，使用后备策略: {xpath}")
            error_element = target_element.locator(f'xpath={xpath}')

        # 关键修改：添加元素存在性检查
        if error_element.count() == 0 :
            # 当预期消息为None时，表示我们期望没有错误提示，此时验证通过
            result = (expected_message is None)
            logger.info(f"定位失败，该元素没有任何错误提示， <返回值>: {result}")
            return result

        else :
            error_text = error_element.text_content().strip()
            # 验证错误提示信息
            if error_text == expected_message:
                logger.info(f"✅ 验证成功：错误提示信息正确，内容为 '{error_text}'")
                return True
            else:
                logger.error(f"错误提示信息不符，预期: '{expected_message}'，实际: '{error_text}'")
                return False

    except AssertionError as ae:
        logger.error(f"错误提示信息时出错: {ae}")
        raise


def wait_dialog_with_expected_message(page: Page, expected_message: str = "") -> Locator:
    """
    等待对话框出现并返回对话框的Locator对象，可选择验证对话框内容

    :param page: Playwright的Page对象
    :param expected_message: 可选，期望在对话框中出现的文本内容
    :return: 对话框的Locator对象
    :raises AssertionError: 当指定了expected_message但对话框内容不包含时抛出
    """
    try:
        # 等待并定位对话框元素
        dialog = page.wait_for_selector('div[role="dialog"]', timeout=5000)
        if not dialog:
            raise AssertionError("未找到对话框元素")

        # 如果指定了期望消息，则验证内容
        if expected_message:
            actual_message = dialog.text_content()
            logger.info(f"期望消息: {expected_message}")
            logger.info(f"实际消息: {actual_message}")

            if expected_message in actual_message:
                logger.info(f"✅ 验证通过: 对话框文本包含 '{expected_message}'")
            else:
                logger.error(f"❌ 验证失败: 对话框文本 '{actual_message}' 不包含 '{expected_message}'")
                raise AssertionError(f"对话框内容不包含期望消息: {expected_message}")

        return dialog

    except AssertionError as ae:
        logger.error(f"验证对话框时出错: {ae}")
        raise
    except TimeoutError:
        logger.error(f"等待对话框超时 (5000ms)")
        raise AssertionError("等待对话框超时")
    except Exception as e:
        logger.error(f"定位对话框时发生异常: {e}")
        raise

def close_dialog(page: Page) -> None:
    """
    关闭对话框

    :param page: Playwright的Page对象
    """
    try:
        # 定位关闭按钮
        close_button = page.get_by_role("button", name="Close")
        # 点击关闭按钮
        close_button.click()
        # 等待关闭按钮隐藏
        close_button.wait_for(state='hidden')
    except Exception as e:
        # 若关闭对话框过程中出现异常，记录错误日志
        logger.error(f"关闭对话框时出错: {e}")

def fill_textbox(page: Page, label: str, value: str) -> None:
    """
    填写文本框

    :param page: Playwright的Page对象
    :param label: 文本框的标签
    :param value: 要填写的值
    """
    try:
        # 定位文本框并填写值
        page.get_by_role("textbox", name=label).fill(value)
    except Exception as e:
        # 若填写文本框过程中出现异常，记录错误日志
        logger.error(f"填写文本框 {label} 时出错: {e}")

def select_option_by_text(page, tip_text, target_text):
    """
    在下拉菜单中选择包含指定文本的选项

    :param page: Playwright的Page对象
    :param tip_text: 下拉菜单的提示文本
    :param target_text: 要选择的目标文本
    :return: 若找到并选择目标选项返回True，否则返回False
    """
    try:
        # 定位到下拉菜单容器并点击
        page.get_by_role("textbox", name="请选择民宿").click()
        time.sleep(1)
        # 定位下拉菜单元素
        dropdown = page.locator(".el-scrollbar")
        # 等待下拉菜单可见
        dropdown.wait_for(state="visible")

        # 定位滚动内容区域和滚动条
        scroll_wrap = dropdown.locator(".el-select-dropdown__wrap")
        scrollbar = dropdown.locator(".el-scrollbar__thumb")

        # 计算滚动步长 (根据实际情况调整)
        scroll_step = 100
        max_scroll_attempts = 10
        scroll_attempt = 0

        while scroll_attempt < max_scroll_attempts:
            # 查找当前可见区域内的选项
            options = dropdown.locator("li.el-select-dropdown__item")
            count = options.count()

            for i in range(count):
                option = options.nth(i)
                text = option.text_content()
                if target_text in text:
                    # 若找到目标选项，点击并返回True
                    option.click()
                    logger.info(f"已选择: {text}")
                    return True

            # 如果未找到，滚动页面
            current_scroll = page.evaluate('(element) => element.scrollTop', scroll_wrap)
            page.evaluate('(element, step) => element.scrollBy(0, step)', scroll_wrap, scroll_step)

            # 等待页面滚动和内容加载
            page.wait_for_timeout(300)

            # 检查是否已滚动到底部
            new_scroll = page.evaluate('(element) => element.scrollTop', scroll_wrap)
            if new_scroll == current_scroll:
                logger.info("已滚动到底部")
                break

            scroll_attempt += 1

        logger.info(f"未找到文本为 '{target_text}' 的选项")
        return False
    except Exception as e:
        # 若选择选项过程中出现异常，记录错误日志并返回False
        logger.error(f"选择选项 {target_text} 时出错: {e}")
        return False

def select_region(page: Page, label: str, province: str, city: str, district: str) -> None:
    """
    选择行政区划

    :param page: Playwright的Page对象
    :param label: 行政区划选择框的标签
    :param province: 省份名称
    :param city: 城市名称
    :param district: 区县名称
    """
    try:
        # 点击行政区划选择框
        page.get_by_role("textbox", name=label).click()
        # 填写行政区划信息
        page.get_by_role("textbox", name=label).fill(f"{province}{city}{district}")
        # 点击第一个列表项
        page.get_by_role("listitem").first.click()
    except Exception as e:
        # 若选择行政区划过程中出现异常，记录错误日志
        logger.error(f"选择行政区划 {province}{city}{district} 时出错: {e}")

def select_radio_button(page: Page, label_text: str, target_option: str) -> None:
    """
    在指定标签下遍历单选按钮，根据文本内容匹配并选择目标选项

    :param page: Playwright 页面对象
    :param label_text: 父级标签文本（如"便器"）
    :param target_option: 目标选项文本（如"智能马桶"）
    :raises ValueError: 未找到匹配的选项
    """
    try:
        # 获取所有相关的单选按钮元素
        radio_buttons = get_label_corresponding_elements(page, label_text, 'following-sibling::div//label')

        # 遍历按钮并匹配文本内容
        for btn in radio_buttons:
            # 获取按钮文本（去除空白）
            btn_text = btn.text_content().strip()

            # 匹配目标选项（支持模糊匹配，如需精确匹配可改为 ==）
            if target_option in btn_text:
                # 点击匹配的按钮
                btn.click()
                logger.info(f"已选择选项：{btn_text}")
                return  # 匹配后立即返回

        # 未找到匹配项时抛出异常
        raise ValueError(f"未找到选项：{target_option}，可用选项为：{[btn.text_content().strip() for btn in radio_buttons]}")
    except Exception as e:
        # 若选择单选按钮过程中出现异常，记录错误日志并抛出异常
        logger.error(f"选择单选按钮 {target_option} 时出错: {e}")
        raise

def is_radio_selected(page: Page, label_text: str, target_option: str) -> bool:
    """
    在指定标签下遍历单选按钮，根据文本内容匹配目标选项并返回选中状态

    :param page: Playwright 页面对象
    :param label_text: 父级标签文本（如"便器"）
    :param target_option: 目标选项文本（如"智能马桶"）
    :return: 目标选项的选中状态
    :raises ValueError: 未找到匹配的选项
    """
    try:
        logger.info(f"开始检查单选按钮: {label_text} > {target_option}")

        # 获取所有相关的单选按钮元素
        radio_labels = get_label_corresponding_elements(page, label_text, 'following-sibling::div//label')

        # 检查是否存在匹配的选项
        matched_btn = None
        for btn in radio_labels:
            btn_text = btn.text_content().strip()
            if target_option in btn_text:
                matched_btn = btn
                break

        if not matched_btn:
            available_options = [btn.text_content().strip() for btn in radio_labels]
            error_msg = f"未找到选项：{target_option}，可用选项为：{available_options}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 获取实际的 input 元素
        input_element = matched_btn.locator('input[type="radio"]')
        if not input_element.count():
            error_msg = f"无法在标签元素中找到对应的单选按钮输入框: {target_option}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # 确认选中状态并记录结果
        is_checked = input_element.is_checked()
        status_icon = "✅" if is_checked else "❌"
        logger.info(f"{status_icon} [{target_option}]状态：{'已选中' if is_checked else '未选中'}")
        return is_checked

    except (ValueError, RuntimeError) as e:
        logger.error(f"检查单选按钮时出错: {str(e)}")
        raise  # 重新抛出特定异常，保持原有行为

    except Exception as e:
        logger.error(f"意外错误: {str(e)}")
        return False  # 非预期异常时返回False，保持原有行为

def set_selector_input_by_label_text(page: Page, label_text, value):
    """
    设置输入框的值

    Args:
        label_text (str): 标签文本
        value (str): 要设置的值
    """
    target_input = get_label_corresponding_element(page, label_text, 'following-sibling::div//input')
    increase_button = get_label_corresponding_element(page, label_text,
                                                      'following-sibling::div//*[contains(@class, "increase")]')
    click_increase_button(increase_button, target_input, value)

def set_selector_input_by_input_element(input_element, xpath, value):
    """
    设置输入框的值

    Args:
        label_text (str): 标签文本
        value (str): 要设置的值
    """

    increase_button = locate_element_by_step_strategy(input_element, xpath)
    click_increase_button(increase_button, input_element, value)

def get_error_elements_with_text(page: Page, text: str) -> list[Locator]:
    """
    查找所有包含 "error" 的 class 元素，并筛选出文本内容包含指定字段的元素

    :param page: Playwright 页面对象
    :param text: 需要在元素文本中查找的字段
    :return: 符合条件的元素定位器列表
    """
    try:
        # 定位所有包含 "error" 的 class 元素
        error_elements = page.locator('[class*="error"]')

        # 筛选出文本内容包含指定字段的元素
        matching_elements = []
        for i in range(error_elements.count()):
            element = error_elements.nth(i)
            if text in element.inner_text().strip():
                matching_elements.append(element)

        return matching_elements
    except Exception as e:
        # 若查找错误元素过程中出现异常，记录错误日志并返回空列表
        logger.error(f"查找包含文本 {text} 的错误元素时出错: {e}")
        return []

def click_increase_button(increase_button, target_input, expected_number):
    """
    点击增加按钮，直到目标输入框中的数字达到预期值

    :param increase_button: 增加按钮的Locator对象
    :param target_input: 目标输入框的Locator对象
    :param expected_number: 预期的数字
    """
    try:
        # 检查expected_number是否为None
        if expected_number is None:
            logger.info("请输入正确的数字")
            return

        # 尝试将预期值转换为整数
        try:
            expected_number = int(expected_number)
        except (ValueError, TypeError):
            logger.info("请输入正确的数字")
            return

        # 获取当前值（处理空字符串的情况）
        try:
            current_number = int(target_input.input_value())
        except ValueError:
            current_number = 0

        # 循环点击增加按钮，直到达到预期值
        while current_number < expected_number:
            increase_button.click()
            # 等待输入框值更新
            time.sleep(0.3)

            # 再次获取值并处理可能的空字符串
            try:
                current_number = int(target_input.input_value())
            except ValueError:
                current_number = 0
    except Exception as e:
        # 若点击增加按钮过程中出现异常，记录错误日志
        logger.error(f"点击增加按钮直到达到 {expected_number} 时出错: {e}")

def check_success_message(page: Page, expected_text, timeout=5000):
    """
    检查页面上是否显示成功消息。

    :param page: Playwright的Page对象
    :param expected_text: 期望的成功消息文本
    :param timeout: 等待元素出现的超时时间（毫秒），默认为5000ms
    :return: 如果找到匹配的成功消息则返回True，否则返回False
    """
    try:
        # 检查必要参数是否为空
        if not expected_text:
            raise ValueError("Expected text is required.")

        # 定位具有role="alert"的元素并检查其文本内容
        alert_element = page.get_by_role("alert")
        alert_element.wait_for(timeout=timeout)
        # 检查元素是否可见且包含期望的文本
        if alert_element.is_visible() and expected_text in alert_element.inner_text():
            return True
        else:
            return False
    except Exception as e:
        # 若检查成功消息过程中出现异常，记录错误日志并返回False
        logger.error(f"检查成功消息 {expected_text} 时出错: {e}")
        return False

def check_alert_text(page: Page, expected_text: str, timeout: int = 5000) -> tuple[bool, str]:
    """
    检查页面上的 alert 元素文本是否与预期文本匹配

    参数:
        page (Page): Playwright 页面对象
        expected_text (str): 期望的 alert 文本内容
        timeout (int, optional): 等待 alert 元素的超时时间(毫秒)，默认5000

    返回:
        tuple[bool, str]: 验证结果和实际文本内容
    """
    actual_text = ""
    try:
        # 等待 alert 元素出现
        alert_element = page.wait_for_selector('[role="alert"]', timeout=timeout)
        if not alert_element:
            logger.info("错误: 未找到 [role='alert'] 元素")
            return False, actual_text

        # 获取 alert 元素的文本内容
        actual_text = alert_element.inner_text()

        # 对比实际文本与预期文本
        if actual_text == expected_text:
            logger.info(f"✅ 验证通过: alert 文本 '{actual_text}' 与预期一致")
            return True, actual_text
        else:
            logger.info(f"❌ 验证失败: 实际文本 '{actual_text}' 与预期 '{expected_text}' 不匹配")
            return False, actual_text

    except TimeoutError:
        logger.info(f"错误: 等待 alert 元素超时 ({timeout}ms)")
        return False, actual_text
    except Exception as e:
        logger.info(f"错误: 获取 alert 文本时发生异常: {str(e)}")
        return False, actual_text

def check_dialog_text(page: Page, expect_message: str) -> tuple[Locator, str]:
    """
    等待对话框出现并验证标题，返回对话框定位器和实际文本内容

    参数:
        page (Page): Playwright 页面对象
        expect_message (str): 期望的对话框文本内容

    返回:
        tuple[Locator, str]: 对话框定位器和实际文本内容

    异常:
        AssertionError: 对话框内容不包含期望的消息
    """
    actual_message = ""
    try:
        # 等待对话框元素出现
        dialog = page.wait_for_selector('div[role="dialog"]', timeout=5000)
        if not dialog:
            logger.error("❌ 验证失败: 未找到对话框元素")
            raise AssertionError("未找到对话框元素")

        # 获取对话框的文本内容
        actual_message = dialog.text_content()
        logger.info(f"期望消息: {expect_message}")
        logger.info(f"实际消息: {actual_message}")

        # 验证消息内容
        if expect_message in actual_message:
            logger.info(f"✅ 验证通过: 对话框文本包含 '{expect_message}'")
            return dialog, actual_message
        else:
            logger.error(f"❌ 验证失败: 对话框文本 '{actual_message}' 不包含 '{expect_message}'")
            raise AssertionError(f"对话框内容不包含期望消息: {expect_message}")

    except TimeoutError:
        logger.error(f"❌ 验证失败: 等待对话框元素超时 (5000ms)")
        raise AssertionError("等待对话框超时")
    except AssertionError as ae:
        # 直接重新抛出断言错误
        raise
    except Exception as e:
        logger.error(f"❌ 验证失败: 获取对话框文本时发生异常: {str(e)}")
        raise AssertionError(f"获取对话框文本异常: {str(e)}")

def wait_alert_text_disappear(page: Page, expected_text: str, timeout: int = 5000) -> bool:
    """
    等待页面上的 alert 元素包含预期文本后消失

    参数:
        page (Page): Playwright 页面对象
        expected_text (str): 期望消失的 alert 文本内容
        timeout (int, optional): 等待超时时间(毫秒)，默认5000

    返回:
        bool: 如果 alert 文本成功消失返回 True，否则返回 False
    """
    try:
        # 等待 alert 元素出现并包含预期文本
        alert_selector = '[role="alert"]'
        page.wait_for_selector(
            f'{alert_selector}:has-text("{expected_text}")',
            timeout=timeout
        )

        # 等待 alert 元素消失或文本变化
        page.wait_for_function(
            f'''() => {{
                const alert = document.querySelector('{alert_selector}');
                return !alert || alert.innerText !== "{expected_text}";
            }}''',
            timeout=timeout
        )
        time.sleep(1)
        logger.info(f"✅ 验证通过: 包含文本 '{expected_text}' 的 alert 元素已消失")
        return True

    except TimeoutError:
        logger.info(f"❌ 验证失败: 等待 alert 消失超时 ({timeout}ms)")
        return False

    except Exception as e:
        logger.info(f"错误: 等待 alert 消失时发生异常: {str(e)}")
        return False

def select_option_by_label_text(page: Page, label_text, option_text):
    """
    选择下拉列表中的选项

    Args:
        label_text (str): 标签文本
        option_text (str): 选项文本
    """
    page.get_by_role("textbox", name=label_text).click()
    page.get_by_role("listitem").filter(has_text=regex_pattern(option_text)).click()

def select_option_by_input_element(page: Page, input_element, option_text=None):
    """
    选择下拉列表中的选项

    Args:
        label_element: 标签元素对象
        option_text (str, optional): 选项文本。默认为None，表示不选择具体选项。
    """
    if option_text is not None and option_text.strip():
        input_element.click()
        page.get_by_role("listitem").filter(has_text=regex_pattern(option_text)).click()
    else:
        print("option_text为空、None或仅包含空白字符，未执行选择操作")

def select_radio(page: Page, label_text, option_text):
    """
    选择单选按钮

    Args:
        label_text (str): 标签文本
        option_text (str): 选项文本
    """
    select_radio_button(page, label_text, option_text)

def simulate_blur(element):
    """
    模拟元素失去焦点的动作

    Args:
        element: 需要模拟失去焦点的元素
    """
    try:
        element.blur()
    except Exception as e:
        # 记录错误但不中断测试
        print(f"警告: 模拟元素失去焦点失败: {e}")

def validate_upload_results(label_types):
    """
    验证文件上传结果

    Args:
        label_types (dict): 房间类型及其上传数据

    Returns:
        dict: 验证结果，包含每个房间类型的上传状态

    Raises:
        AssertionError: 如果有文件未成功上传
    """
    upload_results = {}
    for label_type, data in label_types.items():
        expected = data["expected"]
        actual = data["uploaded"]
        is_complete = expected == actual

        upload_results[label_type] = {
            "expected": expected,
            "actual": actual,
            "is_complete": is_complete
        }

        status = "全部上传成功" if is_complete else "部分上传失败"
        logger.info(f"{label_type.capitalize()} 上传状态: {status} ({actual}/{expected})")

    all_complete = all(result["is_complete"] for result in upload_results.values())
    if not all_complete:
        incomplete_types = [t for t, r in upload_results.items() if not r["is_complete"]]
        raise AssertionError(f"上传未完成: {', '.join(incomplete_types)} 有文件未成功上传")

    return upload_results

def validate_count_results(label_types):
    """
    验证文件输入框数量结果

    Args:
        label_types (dict): 房间类型及其验证数据

    Returns:
        dict: 验证结果，包含每个房间类型的验证状态

    Raises:
        AssertionError: 如果有房间类型的输入框数量不符合预期
    """
    validation_results = {}
    for label_type, data in label_types.items():
        expected = data["param"]
        actual = data["count"]

        # 处理expected为空字符串的情况
        if expected == "":
            expected = 0
        elif isinstance(expected, str) and expected.isdigit():
            expected = int(expected)

        is_valid = expected == actual

        validation_results[label_type] = {
            "expected": expected,
            "actual": actual,
            "is_valid": is_valid
        }

        status = "通过" if is_valid else "失败"
        logger.info(f"{label_type.capitalize()} 验证 {status}: 预期={expected}, 实际={actual}")

    all_valid = all(result["is_valid"] for result in validation_results.values())
    if not all_valid:
        failed_types = [t for t, r in validation_results.items() if not r["is_valid"]]
        raise AssertionError(f"验证失败: {', '.join(failed_types)} 的文件输入框数量不符合预期")

    return validation_results

def calculate_expected_inputs(labels):
    """
    计算预期的文件输入框数量

    Args:
        labels (list): 标签元素列表

    Returns:
        int: 预期的文件输入框数量
    """
    expected = 0
    for label in labels:
        try:
            file_input = label.query_selector('xpath=following-sibling::div').query_selector(
                'xpath=//input[@type="file"]')
            if file_input:
                expected += 1
        except Exception:
            continue
    return expected

def check_page_title(page: Page, expected_title: str, timeout=5000) -> bool:
    """
    检查页面标题是否符合预期。

    :param page: Playwright的Page对象
    :param expected_title: 期望的页面标题文本
    :param timeout: 等待标题加载的超时时间（毫秒），默认为5000ms
    :return: 如果页面标题与预期一致则返回True，否则返回False
    """
    try:
        # 检查必要参数是否为空
        if not expected_title:
            raise ValueError("Expected title is required.")

        # 等待页面标题加载完成（通过轮询检查标题变化）
        start_time = time.time()
        while (time.time() - start_time) * 1000 < timeout:
            current_title = page.title()
            if expected_title == current_title:
                logger.info(f"✅ 页面标题与预期一致，当前标题: {page.title()}")
                return True
            # 短暂休眠后重试
            time.sleep(0.1)

        # 超时后仍未匹配标题
        logger.warning(f"❌ 页面标题与预期不符，当前标题: {page.title()}, 预期标题: {expected_title}")
        return False

    except Exception as e:
        # 若检查页面标题过程中出现异常，记录错误日志并返回False
        logger.error(f" ❌ 检查页面标题 {expected_title} 时出错: {e}")
        return False
