from pydantic import BaseModel
from prompts import SYSTEM_PROMTP, format_ticket_and_reply
from openai import (
    OpenAI,
    RateLimitError,
)
import time
from typing import Dict, Any, List
import pandas as pd
import os


class TicketEvalRequest(BaseModel):
    id: int
    ticket: str
    reply: str


class TicketEvalResponse(BaseModel):
    content_score: int
    content_explanation: str 
    format_score: int
    format_explanation: str



class TicketEvaluator:
    """
    Interface to evaluate tickets using chatGPT
    """
    def __init__(
        self,
        client: OpenAI,
        system_prompt: str,
        model_name: str,
        max_tries: int = 5):

        self.client = client
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.max_tries = max_tries

    def generate_evaluation(
        self,
        request: TicketEvalRequest) -> TicketEvalResponse:
        """
        Evaluate a ticket using chatGPT
        """
        ticket_prompt = format_ticket_and_reply(request.ticket, request.reply)

        messages = [
            {"role": "system", "content": SYSTEM_PROMTP},
            {"role": "user", "content": ticket_prompt},
        ] 

        tries = 0
        while tries < self.max_tries:
            try:
                completion = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=messages,
                response_format=TicketEvalResponse,
                )
                ticket_evaluation = completion.choices[0].message.parsed
                return ticket_evaluation
            except RateLimitError:
                tries += 1
                wait_time = 2 ** tries  # Exponential backoff (2s, 4s, 8s)
                print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        # TODO: This could be a custom RateLimitError! 
        raise Exception("Max retries exceeded. Try again later.")



def evaluation_to_dict(
        request: TicketEvalRequest,
        eval: TicketEvalResponse,
    ) -> Dict[str, Any]:
    return {
        "ticket": request.ticket,
        "reply": request.reply,
        "content_score": eval.content_score,
        "content_explanation": eval.content_explanation,
        "format_score": eval.format_score,
        "format_explanation": eval.format_explanation
    }


def read_tickets(tickets_path: str) -> List[TicketEvalRequest]:
    pd_tickets = pd.read_csv(tickets_path)

    tickets = [
    TicketEvalRequest(id=i, ticket=ticket_str, reply=reply_str)
    for i, (ticket_str, reply_str) in enumerate(zip(pd_tickets['ticket'], pd_tickets['reply']))
          ]
    return tickets


def evaluate_tickets_usecase(
    tickets: List[TicketEvalRequest],
    evaluator: TicketEvaluator,
    output_csv_path: str
):
    output = []
    for ticket in tickets:
        print(f"Evaluating ticket: {ticket.id}")
        try:
            evaluation = evaluator.generate_evaluation(ticket)
        except Exception as e:
            print(f"Failed to evaluate ticket: {ticket.id} due to : {e}")
        fmtd_evaluation = evaluation_to_dict(ticket, evaluation)
        output.append(fmtd_evaluation)
    
    pd_output = pd.DataFrame(output)
    pd_output.to_csv(output_csv_path, index=False)



if __name__ == '__main__':
    from dotenv import load_dotenv, find_dotenv
    env_file = find_dotenv()
    loaded = load_dotenv()
    assert loaded, "Please provide an .env file"
    assert "OPENAI_API_KEY" in os.environ, "Please provide an OPENAI_API_KEY in your .env file"
    
    client = OpenAI()
    evaluator = TicketEvaluator(
        client=client,
        system_prompt=SYSTEM_PROMTP,
        model_name="gpt-4o-2024-08-06")

    TICKETS_CSV_PATH = "tickets.csv"
    OUTPUT_CSV_PATH = "tickets_evaluated.csv"
    assert os.path.exists(TICKETS_CSV_PATH), f"{TICKETS_CSV_PATH} do not exists"
    tickets = read_tickets(TICKETS_CSV_PATH)
    evaluate_tickets_usecase(tickets, evaluator, OUTPUT_CSV_PATH)