SYSTEM_PROMTP = """
You will be given a user-generated ticket and a response from a Large Language Model (LLM) in the following format:

ticket: "Hi, I need your help to find my package"
reply: "Great, how can I asist you today?"


### Task:
Evaluate the correctness of the response based on the following criteria:

1. **Content**: Assess the relevance, correctness, and completeness of the response.
2. **Format**: Evaluate the clarity, structure, and grammar/spelling.

Your output **must** be a JSON object with the following format:

```json
{
  "content_score": int,
  "content_explanation": str,
  "format_score": int,
  "format_explanation": str
}


content_score: A rating from 1 to 5, where 1 represents poor content and 5 represents excellent content.
content_explanation: A brief explanation justifying the content_score.
format_score: A rating from 1 to 5, where 1 represents poor formatting and 5 represents perfect formatting.
format_explanation: A brief explanation justifying the format_score.

Important:
The response must be valid JSON with no additional text or formatting outside the JSON block.
Any explanatory notes should be included within the _explanation fields.

Example:
User Input:

ticket: "Hi, I need your help to find my package"
reply: "Great, how can I asist you today?"

Expected JSON Output:

```json
{
  "content_score": 2,
  "content_explanation": "The response is not helpful; it not address the request.",
  "format_score": 3,
  "format_explanation": "There is a minor spelling mistake ('asist' should be 'assist')."
}
```
""".strip()


def format_ticket_and_reply(ticket: str, reply: str) -> str:
    return f"ticket: {ticket}\nreply: {reply}"
