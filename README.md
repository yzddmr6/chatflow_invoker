## Chatflow Invoker

**Author:** yzddmr6
**Version:** 0.0.1
**Type:** tool

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

There are three input parameters:

* APP ID (required): The APP ID of the Chatflow to be invoked, which can be obtained from the URL of the Chatflow page in Dify.
* Prompt (required): The prompt to be sent.
* Inputs JSON (optional): Input parameters for the start node of the Chatflow, in JSON string format.

### Example

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