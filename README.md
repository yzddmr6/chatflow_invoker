## Chatflow Invoker

**Author:** yzddmr6
**Version:** 0.0.3
**Type:** tool

### Changelog

#### v0.0.3

* Update dify_plugin dependency version

#### v0.0.2

* Added remote Chatflow calls
* Added Conversation ID parameter

#### v0.0.1

* Supported local cross-Chatflow calls

### Background

Currently, Dify does not support multi-Chatflow orchestration or cross-Chatflow invocation. This means that all business logic must be completed within a single Chatflow canvas, which becomes difficult to maintain as scenarios become more complex.

Although Dify provides a workaround by allowing Chatflows to be converted into Workflows and published as Tool nodes, this approach has the following limitations:

* **No support for streaming output:** When a Workflow is invoked as a Tool node, it does not support the original streaming output capability of Chatflow, which affects the user experience.
* **No support for multiple output nodes:** Unlike Chatflow, Workflow does not support multiple output nodes, further limiting data processing and presentation in complex business scenarios.

To address these limitations in multi-Chatflow orchestration, I have developed a plugin called Chatflow Invoker, which enables more flexible and efficient application development with Dify.

### Description

Chatflow Invoker can convert a Chatflow into a node within a process workflow, enabling cross-Chatflow invocation.

It can help you:

* **Achieve modularization of Chatflows:** Break down complex business logic into multiple independent Chatflows, improving code reusability and maintainability.
* **Support cross-Chatflow invocation:** Seamlessly call between different Chatflows to enable more flexible business process orchestration.
* **Maintain streaming output experience:** Ensure that Dify’s original streaming output capability is retained even in multi-Chatflow invocation scenarios.

### Local Chatflow Call

Input Parameters:

* App ID (required): The Chatflow app ID to be called. This can be obtained from the Chatflow page URL in Dify.

* Prompt (required): The prompt to be sent.

* Inputs JSON (optional): Input parameters for the Chatflow start node, in JSON string format.

* Conversation ID (optional): The Chatflow conversation ID. To continue a conversation based on a previous chat log, you must pass the conversation_id of the previous message.

#### Example

Here, a simple scenario is simulated.

First, open the URL of the Chatflow you want to call, and obtain its APP ID.

For example: https://dify/app/f011f58c-b1ce-4a9b-89b2-f39fce8466a8/workflow

Here, `f011f58c-b1ce-4a9b-89b2-f39fce8466a8` is the APP ID.

For the Inputs JSON, set it to receive a parameter from the user.

![image-20250721174829878](./assets/image-20250721174829878.png)

In the reply node, select `stream_output` to obtain streaming output results.

![image-20250721174412582](./assets/image-20250721174412582.png)

Upon testing, the other Chatflow is successfully invoked, and streaming output is supported.

![image-20250721174245191](./assets/image-20250721174245191.png)



### Remote Chatflow Call

To further expand Dify's flexibility, this plugin supports remote Chatflow calls. You're no longer limited to a single Dify instance; you can freely combine them to implement distributed calls based on your business needs.

Input Parameters:

* URL (required): The URL of the remote Dify call you want to make, for example: http://127.0.0.1:5001/v1/chat-messages
* API Key (required): The API key for the remote Chatflow call you want to make. For the first time, you'll need to generate one from the Access API section in the sidebar.

* Prompt (required): The prompt to send.

* Inputs JSON (optional): Input parameters for the Chatflow start node, in JSON string format.

* User (optional): The Chatflow user ID, used to identify the end user for easy retrieval and statistics.

* Conversation ID (optional): The Chatflow conversation ID. To continue a conversation based on a previous chat log, you must pass the conversation_id of the previous message.

Usage Example

![image-20250729163100028](./assets/image-20250729163100028.png)