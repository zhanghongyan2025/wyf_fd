# 网约房智慧安全监管平台自动化测试项目 README

## 项目概述
本项目是针对网约房智慧安全监管平台的自动化测试项目，使用Python和Playwright框架实现。通过一系列测试用例，对平台的注册、登录、民宿管理、房间管理等核心功能进行自动化测试，确保平台的稳定性和正确性。

## 项目结构
```
tests/
├── conftest.py          # pytest的配置文件，定义了一些全局的fixture
├── pages/               # 页面类的实现，封装了各个页面的操作方法
│   ├── home_page.py
│   ├── ly_manage.py
│   ├── login_page.py
│   ├── register_page.py
│   └── room_manage_page.py
├── test_suites/         # 测试用例的实现
│   ├── test.py
│   ├── test_register.py
│   └── test_room_manage.py
└── utils/               # 工具类和辅助函数
    ├── data_generator.py
    ├── file_utils.py
    ├── id_card_validator.py
    └── page_utils.py
```

## 环境准备
### 1. Python环境
确保已经安装Python 3.7及以上版本。可以通过以下命令检查Python版本：
```bash
python --version
```

### 2. 依赖安装
在项目根目录下执行以下命令安装所需的依赖：
```bash
pip install -r requirements.txt
```

### 3. Playwright浏览器驱动
安装Playwright浏览器驱动，执行以下命令：
```bash
playwright install
```

## 配置文件 `conftest.py`
`conftest.py` 文件定义了一些全局的fixture，用于在测试用例中共享资源。以下是主要的配置项：
- `browser`：启动一个Chromium浏览器实例，并在测试结束后关闭。
```python
@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()
```
- `page`：在浏览器中创建一个新页面，并在测试结束后关闭。
```python
@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()
```
- `base_url`：指定测试的基础URL。
```python
@pytest.fixture(scope="session")
def base_url():
    return "http://192.168.40.61:3333"
```
- `suffix_home_url`：指定首页的后缀URL。
```python
@pytest.fixture(scope="session")
def suffix_home_url():
    return "/fangdonghome/home"
```
- `test_user`：指定测试用户的用户名和密码。
```python
@pytest.fixture(scope="session")
def test_user():
    return {
        "username": "hongyan20256",
        "password": "Aa123123!"
    }
```
- `pytest_configure`：注册自定义标记，用于标记注册流程相关的测试用例。
```python
def pytest_configure(config):
    # 注册自定义标记
    config.addinivalue_line(
        "markers",
        "register: 标记注册流程相关的测试用例"
    )
```

## 运行测试
在项目根目录下执行以下命令运行所有测试用例：
```bash
pytest
```
如果需要运行特定的测试用例，可以指定测试文件或测试类：
```bash
pytest tests/test_suites/test_register.py
```

## 主要功能模块
### 注册功能测试
在 `tests/test_suites/test_register.py` 中实现了完整的注册流程测试，包括生成随机测试数据、选择房东类型、填写基本信息、填写企业信息（如果是企业类型）、提交注册表单和检查注册成功信息等步骤。

### 登录功能测试
在 `tests/pages/login_page.py` 中封装了登录页面的操作方法，包括导航到登录页面、填写用户名和密码、点击登录按钮和检查登录错误信息等。

### 民宿管理功能测试
在 `tests/pages/ly_manage.py` 中实现了民宿的批量添加功能，包括登录、导航到民宿管理页面、循环添加多个民宿等步骤。

### 房间管理功能测试
在 `tests/test_suites/test_room_manage.py` 中实现了房间注册功能的测试，包括登录、导航到房间管理页面、填写房间信息、上传文件和提交表单等步骤。

## 工具类和辅助函数
### `tests/utils/file_utils.py`
提供了文件读写的工具函数，如读取JSON文件、写入JSON文件、读取文件所有行、写入文件行列表、创建数据目录、追加信息到CSV文件和读取凭证信息等。

### `tests/utils/page_utils.py`
提供了一些页面操作的辅助函数，如滚动到页面底部、滚动到指定关键字的视图、上传文件、获取标签对应的内容、获取标签对应的错误提示信息、获取标签对应的输入框和元素等。

### `tests/utils/data_generator.py`
提供了生成随机测试数据的函数，如生成随机的统一社会信用代码、手机号码、身份证号码和注册数据等。

### `tests/utils/id_card_validator.py`
提供了身份证号码验证和从远程服务器获取短信验证码的功能。

## 注意事项
1. 测试代码中的一些配置信息（如基础URL、测试用户信息等）需要根据实际情况进行修改。
2. 部分测试用例依赖于模拟短信服务或日志文件来获取验证码，需要确保相应的环境配置正确。
3. 测试过程中可能会因为网络、页面加载等原因出现异常，可以根据日志文件中的错误信息进行排查和修复。