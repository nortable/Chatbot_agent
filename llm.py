import os
from dotenv import load_dotenv
import dashscope
from dashscope.api_entities.dashscope_response import Message
from prompt import user_prompt  # Assuming user_prompt is defined in prompt.py
import json

# Load environment variables from .env file, if applicable
load_dotenv()

class ModelProvider(object):
    def __init__(self):
        self.api_key = os.environ.get("API_KEY")
        self.model_name = os.environ.get("MODEL_NAME")
        self._client = dashscope.Generation()
        self.max_retry = 3

    def chat(self, prompt, chat_history):
        cur_retry = 0
        while cur_retry < self.max_retry:
            cur_retry += 1
            try:
                # Initialize messages with the system prompt
                messages = [Message(role='system', content=prompt)]
                
                # Append chat history
                for history in chat_history:
                    messages.append(Message(role='user', content=history[0]))
                    messages.append(Message(role='assistant', content=history[1]))
                
                # Append the user's current prompt
                messages.append(Message(role='user', content=user_prompt))

                # Call the API
                response = self._client.call(
                    model=self.model_name,
                    api_key=self.api_key,
                    messages=messages
                )
                
                """
                Expected response format:
                {
                    "id": "chatcmpl-...",
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "index": 0,
                            "logprobs": null,
                            "message": {
                                "content": "...",
                                "refusal": null,
                                "role": "assistant",
                                "function_call": null,
                                "tool_calls": null
                            }
                        }
                    ],
                    "created": 1728378945,
                    "model": "qwen-plus",
                    "object": "chat.completion",
                    "service_tier": null,
                    "system_fingerprint": null,
                    "usage": {
                        "completion_tokens": 37,
                        "prompt_tokens": 22,
                        "total_tokens": 59,
                        "completion_tokens_details": null,
                        "prompt_tokens_details": null
                    }
                }
                """

                # Print the raw response for debugging
                # print("Raw response:", response)

                # Check if 'choices' key is present
                #if "choices" not in response or not response["choices"]:
                    #print("No 'choices' found in the response.")
                    #return {}

                # Extract the assistant's reply
                res_content = response["output"]["text"]

                
                # Parse the content if it's a JSON string
                try:
                    content = json.loads(res_content)
                except json.JSONDecodeError:
                    content = res_content  # If not JSON, return the raw content
                return content

            except Exception as err:
                print("Call error: {}".format(err))
                # Optionally, implement a delay before retrying
                # time.sleep(1)
                continue  # Proceed to the next retry attempt

        # If all retries fail, return an empty dictionary or appropriate error message
        return {}
