from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import json

# 导入 logging 和自定义处理器
import logging
from dify_plugin.config.logger_format import plugin_logger_handler

# 使用自定义处理器设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(plugin_logger_handler)


class LocalChatflowInvokerTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        logger.debug(f"tool_parameters: {json.dumps(tool_parameters, ensure_ascii=False)}")

        if not tool_parameters.get("app_id") or not tool_parameters.get("query"):
            logger.error("App ID and query are required")
            raise ValueError("App ID and query are required")

        if tool_parameters.get("inputs_json"):
            try:
                inputs = json.loads(tool_parameters.get("inputs_json"))
            except json.JSONDecodeError:
                logger.error("Inputs JSON is not a valid JSON string")
                raise ValueError("Inputs JSON is not a valid JSON string")
        else:
            inputs = {}

        keep_conversation = tool_parameters.get("keep_conversation", False)
        current_conversation_id=self.session.conversation_id
        app_id=tool_parameters.get("app_id")
        save_key=f"{current_conversation_id}:{app_id}"
        logger.debug(f"save_key: {save_key}")
        sub_conversation_id=''

        if keep_conversation:
            if self.session.storage.exist(save_key):
                sub_conversation_id = self.session.storage.get(save_key).decode("utf-8")
                logger.debug(f"sub_conversation_id already exists: {save_key} === {sub_conversation_id}")
            else:
                logger.debug(f"sub_conversation_id does not exist: {save_key} === {sub_conversation_id}")

        logger.debug(f"sub_conversation_id: {sub_conversation_id}")
        response = self.session.app.chat.invoke(
            app_id=tool_parameters.get("app_id"),
            query=tool_parameters.get("query"),
            inputs=inputs,
            response_mode="streaming",
            conversation_id=sub_conversation_id
        )

        for data in response:
            # logger.debug(f"data: {json.dumps(data, ensure_ascii=False)}")
            
            if data.get("event") == "workflow_started":
                if sub_conversation_id=='':
                    if keep_conversation:
                        sub_conversation_id=data.get("conversation_id", "")
                        logger.debug(f"find sub_conversation_id: {sub_conversation_id}")
                    try:
                        self.session.storage.set(save_key, sub_conversation_id.encode("utf-8"))
                        logger.debug(f"saving sub_conversation_id: {save_key} === {sub_conversation_id}")
                    except Exception as e:
                        logger.error(f"Error saving sub_conversation_id: {e}")

            if data.get("event") == "agent_message" or data.get("event") == "message":
                content = data.get("answer", "")
                logger.debug(f"content: {content}")
                yield self.create_stream_variable_message("stream_output", content)
            if data.get("event") == "error":
                logger.error(f"Error: {data.get('message', 'Unknown error')}")
                raise Exception(data.get("message", "Unknown error"))
           
                
       
