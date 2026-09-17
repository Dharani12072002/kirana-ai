from google import genai

from app.config.settings import settings


TEST_TOOL = {
    "type": "function",
    "name": "find_customer",
    "description": "Find a customer by name.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Customer name to search for.",
            }
        },
        "required": ["query"],
    },
}


def main():
    client = genai.Client(
        api_key=settings.GEMINI_API_KEY,
    )

    print("Testing Gemini function calling...")

    interaction = client.interactions.create(
        model=settings.GEMINI_MODEL,
        input="Find the customer Ravi.",
        tools=[TEST_TOOL],
        generation_config={
            "thinking_level": "low",
            "tool_choice": "any",
        },
        timeout=30,
    )

    print("\nGemini returned:")

    for step in interaction.steps:
        print(step)

        if step.type == "function_call":
            print("\nFUNCTION CALL:")
            print("Name:", step.name)
            print("Arguments:", step.arguments)


if __name__ == "__main__":
    main()