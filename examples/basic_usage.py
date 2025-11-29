"""
Basic usage example for LessTokens SDK
"""

import asyncio
import os
from lesstokens_sdk import LessTokensSDK


async def main():
    # Initialize SDK
    sdk = LessTokensSDK(
        api_key=os.getenv("LESSTOKENS_API_KEY", "your-less-tokens-api-key"), provider="openai"
    )

    # Process prompt
    response = await sdk.process_prompt(
        {
            "prompt": "Explain what artificial intelligence is",
            "llm_config": {
                "api_key": os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
                "model": "gpt-4",
                "temperature": 0.7,
            },
        }
    )

    print("Response:", response.content)
    print(f"Tokens saved: {response.usage.savings}%")
    print(f"Total tokens: {response.usage.total_tokens}")


if __name__ == "__main__":
    asyncio.run(main())
