# Rauda Test Interview

This repository contains the solution to the technical interview for Rauda AI. The task is to evaluate the responses of Large Language Models (LLMs) using OpenAI's API.


## Setup

1. Create and activate a virtual environment, install dependencies:

    ```sh
    python -m venv RAUDA_VENV
    source RAUDA_VENV/bin/activate
    pip install -r requirements.txt
    ```

2. Configure environment variables:
    Create an .env file in the root directory with your OpenAI API key. You can use the provided `.env.sample` file as a template.
    ```
    OPENAI_API_KEY=your-api-key-here
    ```

Ensure that the `tickets.csv` exists.

## Execution
To process all tickets, run:

```sh
python main.py
```

## Test
I wrote a unit test to test the retry mechanism for the rate limit error exception. You can test this functionality using the following command:
```sh
pytest test.py -v
```


## Improvements

If I had more time, I would
- Currently, I’m using Pydantic to define how I want the OpenAI API response to be parsed. However, I would test edge cases to ensure the model always responds in the same format.
- Implement for more unit tests for additional API errors.
- Improve how CSV files are read and written. Right now, I’m using Pandas, but I could use the repository pattern to process tickets more efficiently without having to load everything into memory before writing back to the CSV file.