import os
import sys
import argparse
import json
from dotenv import load_dotenv
from openai import OpenAI
from prompts import system_prompt
from call_function import available_functions, call_function

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")

def main():
    parser = argparse.ArgumentParser(description="chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": args.user_prompt
            }
        ]

    if api_key is None:
        raise RuntimeError("Openrouter api key is not set. Please set the OPENROUTER_API_KEY environment variable.")

    client = OpenAI (
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    for _ in range(20):
        response = client.chat.completions.create (
            model= "openrouter/free",
            messages = messages,
            tools=available_functions,
            temperature = 0
        )

        if response.usage is None:
            raise RuntimeError(
                "The API response did not include usage information."
            )

        responseMessage = response.choices[0].message
        messages.append(responseMessage)

        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")

        if not responseMessage.tool_calls:
            print("Final response:")
            print(responseMessage.content)
            return

        for tool_call in responseMessage.tool_calls:
            if tool_call.type != "function":
                continue
            result_message = call_function(tool_call, args.verbose)
            messages.append(result_message)
        
    sys.exit(1)

if __name__ == "__main__":
    main()