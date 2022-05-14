import pytest, os

from external.xray import XrayConnector

xray = XrayConnector("localhost:8080", "admin", "admin")
XRAY_MARKER = "xray"

def pytest_addoption(parser : pytest.Parser):
    parser.addoption(
        "--env",
        action = "store",
        help = "Environment to run tests against"
    )
    parser.addoption(
        "--key",
        action = "store",
        help = "Test Execution Key for the Cucumber Tests from Jira"
    )
    
def pytest_configure(config : pytest.Config):
    env = config.getoption("env")
    if env:
        print(f"Tests are running on {env} environment.")
    else:
        pytest.exit("You have to declare a enviroment for the tests to start.")
        
    mark = config.getoption("-m").replace(" ", "")
    if mark == XRAY_MARKER:
        exec_key = config.getoption("key")
        if exec_key:
            xray.download_feature(exec_key, save_to = "tests\\xray.feature")
        else:
            pytest.exit(f"When marking a test with {XRAY_MARKER} you must also provide a --key.")
        os.environ["FEATURE_FILE"] = "xray.feature"
    else:
        os.environ["FEATURE_FILE"] = "sample.feature"
    
def pytest_collection_modifyitems(items : list[pytest.Function], config : pytest.Config):
    if config.getoption("-m").replace(" ", "") == XRAY_MARKER:
        exec_key = config.getoption("key")
        run_those = xray.get_test_keys(exec_key)
        for item in items:
            run_this = False
            for mark in item.iter_markers():
                if mark.name in run_those:
                    run_this = True
            if run_this:
                item.add_marker(XRAY_MARKER)
                
def pytest_unconfigure(config : pytest.Config):
    if config.getoption("-m").replace(" ", "") == XRAY_MARKER:
        exec_key = config.getoption("key")
        
        data = config._bddcucumberjson.features.values()
        for value in data:
            value["tags"][0]["name"] = exec_key
            
        xray.upload_result(data)
        
        for issue_key in xray.get_test_keys(exec_key):
            test_run = xray.get_test_run(exec_key, issue_key)
            
            xray.upload_evidence(test_run['id'], "maybe some logs", "logs", "txt")