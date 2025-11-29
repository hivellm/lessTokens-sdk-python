"""
Streaming example for LessTokens SDK
"""

import asyncio
import os
from lesstokens_sdk import LessTokensSDK


async def main():
    sdk = LessTokensSDK(
        api_key=os.getenv("LESSTOKENS_API_KEY", "your-less-tokens-api-key"),
        provider="openai"
    )

    async for chunk in sdk.process_prompt_stream({
        "prompt": "Tell a story about a robot learning to paint",
        "llm_config": {
            "api_key": os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
            "model": "gpt-4",
        }
    }):
        if chunk.done:
            print(f"\n\nTokens saved: {chunk.usage.savings}%")
            print(f"Total tokens: {chunk.usage.total_tokens}")
        else:
            print(chunk.content, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())


