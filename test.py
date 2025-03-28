from main import TicketEvaluator, TicketEvalRequest
from unittest.mock import MagicMock, patch
from openai import RateLimitError, OpenAI
import pytest
from unittest.mock import MagicMock
import httpx


@pytest.fixture()
def client() -> OpenAI:
       client = OpenAI(api_key="not a real api key") 
       return client


def create_fake_rate_limit_error() -> RateLimitError:
    # Create a fake httpx.Response with status 429
    fake_response = MagicMock(spec=httpx.Response)
    fake_response.status_code = 429
    fake_response.headers = {"x-request-id": "fake-request-id"}
    fake_response.content = b'{"error": "Too many requests"}'
    fake_response.json.return_value = {"error": "Too many requests"}

    # Create a fake RateLimitError using the mocked response
    fake_rate_limit_error = RateLimitError("This is a fake exception", response=fake_response, body=None)

    return fake_rate_limit_error


class TestTicketEvaluator:
    @pytest.mark.parametrize("max_tries", [1, 5, 10])
    def test_generate_evaluation_with_failure(
        self,
        client: OpenAI,
        max_tries: int):
        """
        Test sleep time and number of calls when api answers with RateLimitError 
        
        """

        evaluator = TicketEvaluator(
            client=client,
            system_prompt="This is a test",
            model_name="Test",
            max_tries=max_tries)
        
        request = TicketEvalRequest(id=0, ticket="Test ticket", reply="Test Replay")
        fake_rate_limit_error = create_fake_rate_limit_error()

        with patch.object(
            evaluator.client.beta.chat.completions,
            "parse",
            side_effect=fake_rate_limit_error) as mock_api_call, \
            patch("time.sleep") as sleep_mock:

            # make sure it raise an Error
            with pytest.raises(Exception, match="Max retries exceeded. Try again later."):
                evaluator.generate_evaluation(request)
            
            # make sure it was call max_tries times
            assert mock_api_call.call_count == max_tries
            assert sleep_mock.call_count == max_tries

            # make sure the sleep time is correct
            for i, call in enumerate(sleep_mock.mock_calls, start=1):
                assert call.args[0] == 2 ** i






