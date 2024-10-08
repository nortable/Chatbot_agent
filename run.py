import time
from tools import tools_map
from prompt import gen_prompt
from llm import ModelProvider

mp = ModelProvider()

def main():
    # Multiple interactions
    max_retry = 10
    while True:
        query = input("Please enter your goal (type 'exit' to quit): ")
        if query.lower() == "exit":
            return
        agent_execute(query, max_retry)

def parse_thoughts(response):
    try:
        thoughts = response.get("thoughts", {})
        plan = thoughts.get("plan", "")
        reasoning = thoughts.get("reasoning", "")
        criticism = thoughts.get("criticism", "")
        speak = thoughts.get("speak", "")
        prompt = f"Plan: {plan}\nReasoning: {reasoning}\nCriticism: {criticism}\nSpeak: {speak}"
        return prompt
    except Exception as err:
        print(f"Error parsing thoughts: {err}")
        return ""


# 在 run.py 中，更新 agent_execute 函数
def agent_execute(query, max_retry=10):
    cur_request = 0
    chat_history = []
    agent_scratch = ''
    final_answer = None

    while cur_request < max_retry:
        cur_request += 1
        # Generate the prompt
        prompt = gen_prompt(query, agent_scratch)

        # Add this line to print the prompt
        print(f"\n*** Prompt for Attempt {cur_request} ***\n{prompt}\n")

        start_time = time.time()
        print(f"*** Attempt {cur_request}: Calling the model ***", flush=True)

        # Call the model
        response = mp.chat(prompt, chat_history)
        end_time = time.time()
        print(f"*** Attempt {cur_request}: Model call finished. Time taken: {end_time - start_time:.2f} seconds ***", flush=True)
        print(response)

        if not response or not isinstance(response, dict):
            print("Error: Invalid response. Waiting to retry...", response)
            continue

        # Extract action information
        action_info = response.get("action", {})
        action_name = action_info.get('name')
        action_args = action_info.get('args', {})
        print(f"Current action name and parameters: {action_name}, {action_args}")

        # Check for finish condition
        if action_name == "finish":
            final_answer = response.get("answer", "")
            if not final_answer:
                final_answer = action_args.get("answer", "")
            print(f"Final Answer: {final_answer}")
            break

        # Execute the action
        try:
            func = tools_map.get(action_name)
            if func:
                observation = func(**action_args)
            else:
                observation = f"Action '{action_name}' is not recognized."
            print(f"Observation: {observation}")
        except Exception as err:
            observation = f"Error executing action '{action_name}': {err}"
            print(observation)

        # Parse assistant's thoughts
        assistant_message = parse_thoughts(response)

        # Update agent scratchpad with the action, observation, and assistant's thoughts
        agent_scratch += f"\nAction taken: {action_name}, with arguments: {action_args}\nObservation: {observation}\nThoughts:\n{assistant_message}"

        # Update chat history
        # Use the assistant's thoughts and observation as the last exchange
        chat_history.append([assistant_message, observation])

    if final_answer:
        print(f"Agent's Final Answer:\n{final_answer}")
    else:
        print("Failed to reach a final answer within the maximum number of retries.")


if __name__ == "__main__":
    main()
