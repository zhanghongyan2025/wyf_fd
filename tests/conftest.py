import pytest
import logging
from playwright.sync_api import sync_playwright
import os
import pytest
from datetime import datetime

# 确保截图目录存在
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """钩子函数：捕获测试结果并在失败时截图"""
    # 获取测试结果报告
    outcome = yield
    report = outcome.get_result()

    # 只处理测试用例失败的情况，且测试函数需要page参数
    if report.when == "call" and report.failed and "page" in item.fixturenames:
        # 获取page对象
        page = item.funcargs["page"]

        # 生成唯一的截图文件名（包含时间戳和测试用例名）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = item.nodeid.replace("::", "_").replace("/", "_")
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"failed_{test_name}_{timestamp}.png")

        # 保存截图
        page.screenshot(path=screenshot_path)
        print(f"\n测试失败，已保存截图至：{screenshot_path}")

@pytest.fixture(autouse=True)
def configure_logging():
    # 配置基本日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 获取你使用的日志记录器
    logger = logging.getLogger('your_logger_name')  # 替换为实际使用的logger名称

    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # 可选：如果pytest拦截输出，可设置不捕获日志
    # 参考：https://docs.pytest.org/en/stable/how-to/capture-warnings.html#accessing-warnings-via-fixtures

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()

@pytest.fixture(scope="session")
def base_url():
    return "http://192.168.40.61:3333"

@pytest.fixture(scope="session")
def suffix_home_url():
 return"/fangdonghome/home"

@pytest.fixture(scope="session")
def test_user():
    return {
        "username": "fenghuang_456",
        "password": "Aa123123!"
    }

# conftest.py
def pytest_configure(config):
    # 注册自定义标记
    config.addinivalue_line(
        "markers",
        "register: 标记注册流程相关的测试用例"
    )



