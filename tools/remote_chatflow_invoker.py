from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import json
import requests

debug=False

class RemoteChatflowInvokerTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        if debug:
            print(tool_parameters)
        if not tool_parameters.get("url_base") or not tool_parameters.get("api_key") or not tool_parameters.get("query"):
            raise ValueError("URL base, API key and query are required")

        if tool_parameters.get("inputs_json"):
            try:
                inputs = json.loads(tool_parameters.get("inputs_json"))
            except json.JSONDecodeError:
                raise ValueError("Inputs JSON is not a valid JSON string")
        else:
            inputs = {}

        url = tool_parameters.get('url_base')
        keep_conversation = tool_parameters.get("keep_conversation", False)
        current_conversation_id=self.session.conversation_id
        app_id=tool_parameters.get("app_id")
        save_key=f"{current_conversation_id}:{app_id}"
        print("save_key: ", save_key)
        sub_conversation_id=''

        if keep_conversation:
            if self.session.storage.exist(save_key):
                sub_conversation_id = self.session.storage.get(save_key).decode("utf-8")
                print(f"sub_conversation_id already exists: {save_key} === {sub_conversation_id}")
            else:
                print(f"sub_conversation_id does not exist: {save_key} === {sub_conversation_id}")

        print("sub_conversation_id: ", sub_conversation_id)

        headers = {
            "Authorization": f"Bearer {tool_parameters.get('api_key')}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": tool_parameters.get("query"),
            "inputs": inputs,
            "response_mode": "streaming",
            "conversation_id": sub_conversation_id,
            "user": tool_parameters.get("user", "")
        }
        with requests.post(url, headers=headers, json=payload, stream=True) as response:
            if response.status_code == 200:
                for line in response.iter_lines():
                    try:
                        line = line.decode("utf-8")
                        prefix = "data: "
                        if line.startswith(prefix):
                            new_line = line[len(prefix) :]
                            data=json.loads(new_line)
                            if data.get("event") == "workflow_started":
                                if sub_conversation_id=='':
                                    if keep_conversation:
                                        sub_conversation_id=data.get("conversation_id", "")
                                        print("find sub_conversation_id: ", sub_conversation_id)
                                    try:
                                        self.session.storage.set(save_key, sub_conversation_id.encode("utf-8"))
                                        print(f"saving sub_conversation_id: {save_key} === {sub_conversation_id}")
                                    except Exception as e:
                                        print(f"Error saving sub_conversation_id: {e}")
                            if data.get("event") == "agent_message" or data.get("event") == "message":
                                content = data.get("answer", "")
                                if debug:
                                    print("data: ", json.dumps(data, ensure_ascii=False))
                                    print("content: ", content)
                                yield self.create_stream_variable_message("stream_output", content)
                            if data.get("event") == "error":
                                if debug:
                                    print(json.dumps(data, ensure_ascii=False))
                                raise Exception(data.get("message", "Unknown error"))
                            
                                
                    except json.JSONDecodeError as e:
                        if debug:
                            print(f"Error decoding JSON: {e}")
                        continue
            else:
                raise Exception(
                    f"Request failed with status code {response.status_code}: {response.text}"
                )
