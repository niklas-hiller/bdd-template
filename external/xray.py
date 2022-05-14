import base64
import os
import requests
import json
import re
import zipfile
import io

class XrayConnector:
    
    def __init__(self, root_url, username, password):
        self._root_url = root_url
        self._username = username
        self._password = password
            
        self._cache = ".xray_cache/"
        
        if not os.path.exists(self.cache):
            os.mkdir(self.cache)
            
    @property
    def root_url(self):
        return self._root_url
    
    @property
    def username(self):
        return self._username
    
    @property
    def password(self):
        return self._password
    
    @property
    def cache(self):
        return self._cache
    
    def auth(self):
        return self.username, self.password
    
    def clear_cache(self):
        for file in os.listdir(self.cache):
            os.remove(f"{self.cache}{os.sep}{file}")
    
    def upload_result(self, data : dict) -> bool:
        if isinstance(data, list) or isinstance(data, dict):
            data_bytes = json.dumps(data).encode("utf-8")
            send_this = io.BytesIO(data_bytes)
        else:
            send_this = open(data, "rb")
        response = requests.post(
            url = f"{self.root_url}/jira/rest/raven/1.0/import/execution/cucumber",
            data = send_this,
            headers = {"Content-type": "application/json"},
            auth = self.auth()
        )
        return response.status_code == 200
    
    def upload_evidence(self, id : str, data : str, filename : str, filetype : str) -> bool:
        data_bytes = data.encode("utf-8")
        base64_bytes = base64.b64encode(data_bytes)
        data_base64 = base64_bytes.decode("utf-8")
        response = requests.put(
            url = f"{self.root_url}/jira/rest/raven/2.0/api/testrun/{id}",
            json = {
                "comment": "This test run was edited by the test automation script",
                "evidences": {
                    "add": [
                        {
                            "data": data_base64,
                            "filename": f"{filename}.{filetype}",
                            "contentType": "application/json" if filetype == "json" else "plain/text"
                        }
                    ]
                }
            },
            headers = {"Content-type": "application/json"},
            auth = self.auth()
        )
        return response.status_code == 200
        
    def get_test_run(self, exec_key : str, issue_key : str) -> dict:
        response = requests.get(
            url = f"{self.root_url}/jira/rest/raven/1.0/api/testrun",
            params = {"testExecIssueKey": exec_key, "testIssueKey": issue_key},
            headers = {"Content-type": "application/json"},
            auth = self.auth()
        )
        if response.status_code != 200: return
        
        return json.loads(response.text)
    
    def get_test_keys(self, test_exec_key : str) -> list:
        response = requests.get(
            url = f"{self.root_url}/jira/rest/raven/1.0/api/testexec/{test_exec_key}/test",
            auth = self.auth()
        )
        if response.status_code != 200: return []
        response_json = json.loads(response.text)
        
        return [test["key"] for test in response_json]
        
    def download_feature(self, test_exec_key : str, save_to : str) -> bool:
        response = requests.get(
            url = f"{self.root_url}/jira/rest/raven/1.0/export/test",
            params = {"keys": test_exec_key, "fz": True},
            auth = self.auth(),
            allow_redirects = True
        )
        if response.status_code != 200: return False
        
        self.clear_cache()
        filename = re.findall("filename=(.+)", response.headers.get("content-disposition"))
        filename = filename[0].replace('"', "")
        path = f"{self.cache}{os.sep}{filename}"
        with open(path, "wb") as file:
            file.write(response.content)
            
        zipfile.ZipFile(path, "r").extractall(
            f"{self.cache}{os.sep}"
        )
        
        features = []
        for feature in os.listdir(f"{self.cache}{os.sep}"):
            if feature.endswith(".feature"):
                features.append(feature)
        
        self.construct(features, test_exec_key, save_to)
        
        return True
        
    def construct(self, features : list, test_exec_key : str, save_to : str):
        test_exec_key = "@" + test_exec_key
        content = [test_exec_key, "Feature: Default", "\n"]
        for _feature in features:
            file_to_open = (
                f"{self.cache}{os.sep}{_feature}"
            )
            with open(file_to_open, "r") as feature:
                raw = feature.read()
                rows = raw.split("\n")
                tracked_scenario = False
                started = False
                free_line = False
                for current in range(len(rows)):
                    if not started:
                        if rows[current].startswith("Feature"):
                            started = True
                        continue
                    formatted = rows[current].replace("\t", "")
                    if formatted.startswith("#"):
                        continue
                    elif formatted == "":
                        if not free_line:
                            content.append("\n")
                            free_line = True
                    elif formatted.startswith("Scenario Outline"):
                        if tracked_scenario:
                            content.append("\n")
                        content.append(rows[current - 1].split(" ")[0])
                        content.append(rows[current])
                        tracked_scenario = True
                    elif tracked_scenario and not formatted.startswith("@"):
                        content.append(rows[current])

        with open(save_to, "a+") as file:
            for row in content:
                if row != test_exec_key:
                    file.write("\n")
                file.write(row)
            file.close()