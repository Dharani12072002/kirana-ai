from groq import Groq

from app.config.settings import settings


def main():
    client = Groq(
        api_key=settings.GROQ_API_KEY
    )

    print("Sending request to Groq...")

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: KiranaAI Groq connection successful."
            }
        ],
    )

    print("\n--- Groq response ---")
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()