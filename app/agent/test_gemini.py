from google import genai

from app.config.settings import settings


def main():
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    interaction = client.interactions.create(
        model=settings.GEMINI_MODEL,
        input="Reply with exactly: KiranaAI Gemini connection successful.",
    )

    print(interaction.output_text)


if __name__ == "__main__":
    main()