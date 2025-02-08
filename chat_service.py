from openai import AsyncOpenAI
from typing import List, Dict, Optional
from googleapiclient.discovery import build
import os
import json
from datetime import datetime


class ChatInterface:
    _instance = None  # Singleton instance
    _initialized = False

    def __new__(cls, openai_api_key: str = None):
        if cls._instance is None:
            cls._instance = super(ChatInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self, openai_api_key: str = None):
        if not self._initialized:
            self.client = AsyncOpenAI(api_key=openai_api_key or os.getenv('OPENAI_API_KEY'))
            self.google_api_key = os.getenv('GOOGLE_API_KEY')
            self.google_cse_id = os.getenv('GOOGLE_CSE_ID')
            self.messages: List[Dict[str, str]] = [
                {
                    "role": "system",
                    "content": """You are a helpful assistant with real-time search capabilities.
                    For current events like elections and live updates:
                    1. Extract and present specific numbers, statistics, and concrete data from the search results
                    2. If you find actual numbers or results, present them directly
                    3. Only if no concrete data is found, then suggest checking specific sources
                    4. Focus on extracting actionable information from the search results rather than just linking to sources
                    5. For election results, prioritize reporting specific vote counts, seats won, and percentages if available

                    Keep your responses focused on the actual data found. If you find real numbers or results, lead with those.
                    Maintain conversation context and update information when asked for the latest."""
                }
            ]
            self._initialized = True

    async def search_google(self, query: str) -> Optional[str]:
        """
        Perform a Google search using Custom Search API
        Args:
            query (str): Search query
        Returns:
            str: Formatted search results or None if search fails
        """
        try:
            service = build(
                "customsearch", "v1",
                developerKey=self.google_api_key,
                static_discovery=False
            )

            # Enhance the search query to target current results
            enhanced_query = f"{query} latest results live updates"

            # Execute search with more specific parameters
            result = service.cse().list(
                q=enhanced_query,
                cx=self.google_cse_id,
                num=5,  # Increased number of results
                dateRestrict='h1',  # Restrict to last hour
                sort='date'  # Sort by date
            ).execute()

            if 'items' not in result:
                return None

            formatted_results = []
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Extract and format the most relevant data
            for item in result['items']:
                # Look for specific data patterns in the title and snippet
                title = item['title']
                snippet = item['snippet']

                # Clean and format the data
                content = f"Source: {title}\n"
                # Extract numbers and statistics if present
                if any(char.isdigit() for char in snippet):
                    content += f"Details: {snippet}\n"

                formatted_results.append(
                    f"{content}"
                    f"Last Updated: {current_time}\n"
                    f"Direct Link: {item['link']}\n"
                )

            return "\n---\n".join(formatted_results)

        except Exception as e:
            print(f"Google Search error: {str(e)}")
            return None

    async def get_response(self, user_input: str) -> str:
        """
        Get a response from the assistant while maintaining conversation history
        Args:
            user_input (str): The user's input/question
        Returns:
            str: The assistant's response
        """
        try:
            # Add user message to history
            self.messages.append({"role": "user", "content": user_input})

            # Perform Google search for relevant information
            search_results = await self.search_google(user_input)
            if search_results:
                self.messages.append({
                    "role": "system",
                    "content": f"Here are relevant search results for the query:\n{search_results}"
                })

            # Get response from GPT-4
            response = await self.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=self.messages,
                temperature=0.7,
                max_tokens=2000
            )

            # Extract and store assistant's response
            assistant_message = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": assistant_message})

            # Debug: Print conversation length
            print(f"Conversation history length: {len(self.messages)} messages")

            return assistant_message

        except Exception as e:
            print(f"Error getting response from OpenAI: {str(e)}")
            raise Exception(f"Failed to get AI response: {str(e)}")

    def clear_history(self):
        """Clear chat history except for the system message"""
        self.messages = [self.messages[0]]
        print("Conversation history cleared")

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history"""
        return self.messages


# Create a singleton instance
_chat_interface = None


def get_chat_interface() -> ChatInterface:
    """Get or create the singleton ChatInterface instance"""
    global _chat_interface
    if _chat_interface is None:
        _chat_interface = ChatInterface(openai_api_key=os.getenv('OPENAI_API_KEY'))
    return _chat_interface


async def handle_get_response_for_user(text_content: str) -> str:
    """
    Wrapper function to get response from ChatInterface
    Args:
        text_content (str): The text to send to the AI
    Returns:
        str: The AI's response
    """
    try:
        # Use the singleton instance
        chat_interface = get_chat_interface()
        response = await chat_interface.get_response(text_content)
        return response
    except Exception as e:
        raise Exception(f"Failed to get response: {str(e)}")