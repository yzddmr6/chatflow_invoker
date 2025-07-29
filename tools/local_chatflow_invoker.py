from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import json

debug=False

class LocalChatflowInvokerTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        if debug:
            print(tool_parameters)
            
        if not tool_parameters.get("app_id") or not tool_parameters.get("query"):
            raise ValueError("App ID and query are required")

        if tool_parameters.get("inputs_json"):
            try:
                inputs = json.loads(tool_parameters.get("inputs_json"))
            except json.JSONDecodeError:
                raise ValueError("Inputs JSON is not a valid JSON string")
        else:
            inputs = {}

        response = self.session.app.chat.invoke(
            app_id=tool_parameters.get("app_id"),
            query=tool_parameters.get("query"),
            inputs=inputs,
            response_mode="streaming",
            conversation_id=tool_parameters.get("conversation_id", "")  # 可选，留空则创建新对话
        )

        for data in response:
            if data.get("event") == "agent_message" or data.get("event") == "message":
                content = data.get("answer", "")
                if debug:
                    print(json.dumps(data, ensure_ascii=False))
                    print(content)
                yield self.create_stream_variable_message("stream_output", content)
