from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import json
import requests

# 导入 logging 和自定义处理器
import logging
from dify_plugin.config.logger_format import plugin_logger_handler

# 使用自定义处理器设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)
logger.addHandler(plugin_logger_handler)   

class RemoteChatflowInvokerTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        logger.info(f"tool_parameters: {json.dumps(tool_parameters, ensure_ascii=False)}")
        if not tool_parameters.get("url_base") or not tool_parameters.get("api_key") or not tool_parameters.get("query"):
            logger.error("URL base, API key and query are required")
            raise ValueError("URL base, API key and query are required")

        if tool_parameters.get("inputs_json"):
            try:
                inputs = json.loads(tool_parameters.get("inputs_json"))
            except json.JSONDecodeError:
                logger.error("Inputs JSON is not a valid JSON string")
                raise ValueError("Inputs JSON is not a valid JSON string")
        else:
            inputs = {}

        url = tool_parameters.get('url_base')
        keep_conversation = tool_parameters.get("keep_conversation", False)

        sub_conversation_id=''

        if keep_conversation:
            current_conversation_id=self.session.conversation_id
            app_id=tool_parameters.get("app_id")
            save_key=f"{current_conversation_id}:{app_id}"
            logger.info(f"save_key: {save_key}")
            
            if self.session.storage.exist(save_key):
                sub_conversation_id = self.session.storage.get(save_key).decode("utf-8")
                logger.info(f"sub_conversation_id already exists: {save_key} === {sub_conversation_id}")
            else:
                logger.info(f"sub_conversation_id does not exist: {save_key} === {sub_conversation_id}")

        logger.info(f"sub_conversation_id: {sub_conversation_id}")

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
                            logger.debug(f"new_line: {new_line}")
                            data=json.loads(new_line)
                            if data.get("event") == "workflow_started":
                                if sub_conversation_id=='':
                                    if keep_conversation:
                                        sub_conversation_id=data.get("conversation_id", "")
                                        logger.info(f"find sub_conversation_id: {sub_conversation_id}")
                                        try:
                                            self.session.storage.set(save_key, sub_conversation_id.encode("utf-8"))
                                            logger.info(f"saving sub_conversation_id: {save_key} === {sub_conversation_id}")
                                        except Exception as e:
                                            logger.error(f"Error saving sub_conversation_id: {e}")
                            if data.get("event") == "agent_message" or data.get("event") == "message":
                                content = data.get("answer", "")
                                logger.debug(f"content: {content}")
                                yield self.create_stream_variable_message("stream_output", content)
                            if data.get("event") == "error":
                                logger.debug(f"data: {json.dumps(data, ensure_ascii=False)}")
                                raise Exception(data.get("message", "Unknown error"))
                            
                                
                    except json.JSONDecodeError as e:
                        logger.error(f"Error decoding JSON: {e}")
                        continue
            else:
                raise Exception(
                    f"Request failed with status code {response.status_code}: {response.text}"
                )
