from groq import Groq

from app.config.settings import settings
from app.agent.tools import execute_tool


def main():
    client = Groq(
        api_key=settings.GROQ_API_KEY
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "find_customer",
                "description": (
                    "Find customers in the supermarket customer database "
                    "by customer name or phone number."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Customer name or phone number to search for."
                            ),
                        }
                    },
                    "required": ["query"],
                },
            },
        }
    ]

    messages = [
        {
            "role": "system",
            "content": (
                "You are KiranaAI, an AI assistant for an Indian "
                "supermarket owner. Use available tools when database "
                "information is required."
            ),
        },
        {
            "role": "user",
            "content": "Find the customer Ravi.",
        },
    ]

    print("Sending request to Groq...")

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message

    print("\n--- Groq response ---")

    if not assistant_message.tool_calls:
        print(assistant_message.content)
        return

    for tool_call in assistant_message.tool_calls:

        tool_name = tool_call.function.name
        arguments = tool_call.function.arguments

        print("\n--- Tool requested by Groq ---")
        print("Tool:", tool_name)
        print("Arguments:", arguments)

        import json

        arguments = json.loads(arguments)

        result = execute_tool(
            tool_name,
            arguments,
        )

        print("\n--- Python tool result ---")
        print(result)

        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                ],
            }
        )

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            }
        )

    final_response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    print("\n--- Final Groq response ---")
    print(final_response.choices[0].message.content)


if __name__ == "__main__":
    main()