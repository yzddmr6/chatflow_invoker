from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import json
import requests
from jsonpath_ng import parse

debug=False

class UniversalChatflowInvokerTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        if debug:
            print(json.dumps(tool_parameters, ensure_ascii=False))
        if not tool_parameters.get("url_base") or \
        not tool_parameters.get("body_json") or \
        not tool_parameters.get("json_path"):
            raise ValueError("URL base, header JSON, body JSON and JSON path are required")

        if tool_parameters.get("header_json"):
            try:
                header_json = json.loads(tool_parameters.get("header_json"))
            except json.JSONDecodeError:
                raise ValueError("Header JSON is not a valid JSON string")
        else:
            header_json = {}

        try:
            body_json = json.loads(tool_parameters.get("body_json"))
        except json.JSONDecodeError:
            raise ValueError("Body JSON is not a valid JSON string")

        url = tool_parameters.get('url_base')
        json_path = tool_parameters.get("json_path")

        header_json["Content-Type"] = "application/json"
        
        with requests.post(url, headers=header_json, json=body_json, stream=True, allow_redirects=True) as response:
            if response.status_code == 200:
                for line in response.iter_lines():
                    try:
                        line = line.decode("utf-8")
                        # 查找第一个 "data:" 的位置
                        prefix = "data:"
                        prefix_index = line.find(prefix)
                        if prefix_index != -1:
                            # 提取从 "data:" 之后的JSON内容
                            json_content = line[prefix_index + len(prefix):]
                            data = json.loads(json_content.strip()) # OpenAI有空格，百炼没有空格
                            if debug:
                                print(json.dumps(data, ensure_ascii=False))
                            json_path_expr = parse(json_path)
                            result = json_path_expr.find(data)
                            if result:
                                for match in result:
                                    yield self.create_stream_variable_message("stream_output", match.value)
                    except json.JSONDecodeError as e:
                        continue
            else:
                raise Exception(
                    f"Request failed with status code {response.status_code}: {response.text}"
                )