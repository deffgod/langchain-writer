import asyncio

from langchain_writer import ChatWriter


def sync_example():
    print("\n=== Synchronous Example ===")
    llm = ChatWriter()

    # Basic invoke example
    print("\n1. Basic invoke:")
    response = llm.invoke("Write a haiku about programming.")
    print(response)

    # Streaming example
    print("\n2. Streaming response:")
    for chunk in llm.stream("Explain what a neural network is in 3 sentences."):
        print(chunk, end="", flush=True)
    print("\n")


async def async_example():
    print("\n=== Asynchronous Example ===")
    llm = ChatWriter()

    # Basic async invoke
    print("\n1. Basic async invoke:")
    response = await llm.ainvoke(
        "What is the difference between Python and JavaScript?"
    )
    print(response)

    # Async streaming
    print("\n2. Async streaming response:")
    async for chunk in llm.astream("Explain quantum computing in simple terms."):
        print(chunk, end="", flush=True)
    print("\n")


def main():
    print("Testing ChatWriter Functionality\n")
    print("--------------------------------")

    # Run sync examples
    sync_example()

    # Run async examples
    asyncio.run(async_example())

    print("\nAll examples completed!")


if __name__ == "__main__":
    main()
