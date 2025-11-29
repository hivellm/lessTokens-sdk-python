"""
Multi-turn conversation example for LessTokens SDK
"""

import asyncio
import os
from lesstokens_sdk import LessTokensSDK


async def main():
    sdk = LessTokensSDK(
        api_key=os.getenv("LESSTOKENS_API_KEY", "your-less-tokens-api-key"),
        provider="openai"
    )

    # First message
    response1 = await sdk.process_prompt({
        "prompt": "What is the capital of France?",
        "llm_config": {
            "api_key": os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
            "model": "gpt-4",
        }
    })

    print("User: What is the capital of France?")
    print(f"Assistant: {response1.content}\n")

    # Second message with conversation history
    response2 = await sdk.process_prompt({
        "prompt": "What is its population?",
        "llm_config": {
            "api_key": os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
            "model": "gpt-4",
        },
        "messages": [
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": response1.content},
        ]
    })

    print("User: What is its population?")
    print(f"Assistant: {response2.content}")


if __name__ == "__main__":
    asyncio.run(main())


