from app.agent.agent import KiranaAgent


def main():

    agent = KiranaAgent()

    print("KiranaAI started.")
    print("Type 'exit' to stop.\n")

    while True:

        user_message = input("Shopkeeper: ")

        if user_message.lower().strip() == "exit":
            break

        response = agent.run(user_message)

        print("\nKiranaAI:", response)
        print()


if __name__ == "__main__":
    main()