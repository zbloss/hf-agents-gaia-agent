import requests
from smolagents import CodeAgent
from tqdm import tqdm
from prompts.default_prompt import generate_prompt

DEFAULT_API_URL: str = "https://agents-course-unit4-scoring.hf.space"


def get_questions(questions_endpoint: str = "/questions") -> list[dict]:
    """
    Fetches questions from the specified endpoint.

    Args:
        questions_endpoint (str): The endpoint to fetch questions from.

    Returns:
        list[dict]: A list of questions in JSON format.
    """

    api_url = DEFAULT_API_URL + questions_endpoint
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        questions_data = response.json()
        if not questions_data:
            print("Fetched questions list is empty.")
            return []
        print(f"Fetched {len(questions_data)} questions.")
        return questions_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching questions: {e}")
        return []
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error decoding JSON response from questions endpoint: {e}")
        return []


def run_agent(agent: CodeAgent, questions: list[dict]) -> list[str]:
    """
    Runs the agent on the provided questions.

    Args:
        agent (CodeAgent): The agent to run.
        questions (list[str]): A list of questions to be answered.

    Returns:
        list[str]: A list of answers from the agent.
    """
    results_log = []
    answers_payload = []
    for question in tqdm(questions, desc="Running agent"):
        task_id = question.get("task_id")
        question_text = question.get("question")
        file_name = question.get("file_name")
        prompt = generate_prompt(question_text, file_name)

        if not task_id or question_text is None:
            print(f"Skipping item with missing task_id or question: {question}")
            continue

        try:
            answer = agent(prompt)
            answers_payload.append({"task_id": task_id, "submitted_answer": answer})
            results_log.append(
                {
                    "Task ID": task_id,
                    "Question": question_text,
                    "Submitted Answer": answer,
                }
            )
        except Exception as e:
            print(f"Error running agent on task '{task_id}': {e}")
            results_log.append(
                {
                    "Task ID": task_id,
                    "Question": question_text,
                    "Submitted Answer": f"AGENT ERROR: {e}",
                }
            )
    if not answers_payload:
        print("Agent did not produce any answers to submit.")
        return results_log
    return answers_payload


def submit_answers(
    answers_payload: list[dict],
    submission_endpoint: str = "/submit",
    username: str = "altozachmo",
) -> str:
    """
    Submits the answers to the specified endpoint.
    """

    agent_code = f"https://huggingface.co/spaces/{username}/tree/main"
    submission_data = {
        "username": username.strip(),
        "agent_code": agent_code.strip(),
        "answers": answers_payload,
    }
    submit_url: str = DEFAULT_API_URL + submission_endpoint
    try:
        response = requests.post(submit_url, json=submission_data, timeout=60)
        response.raise_for_status()
        result_data = response.json()
        final_status = (
            f"Submission Successful!\n"
            f"User: {result_data.get('username')}\n"
            f"Overall Score: {result_data.get('score', 'N/A')}% "
            f"({result_data.get('correct_count', '?')}/{result_data.get('total_attempted', '?')} correct)\n"
            f"Message: {result_data.get('message', 'No message received.')}"
        )
        print("Submission successful.")
        return final_status
    except requests.exceptions.HTTPError as e:
        error_detail = f"Server responded with status {e.response.status_code}."
        try:
            error_json = e.response.json()
            error_detail += f" Detail: {error_json.get('detail', e.response.text)}"
        except requests.exceptions.JSONDecodeError:
            error_detail += f" Response: {e.response.text[:500]}"
        status_message = f"Submission Failed: {error_detail}"
        print(status_message)
        return status_message
    except requests.exceptions.Timeout:
        status_message = "Submission Failed: The request timed out."
        print(status_message)
        return status_message
    except requests.exceptions.RequestException as e:
        status_message = f"Submission Failed: Network error - {e}"
        print(status_message)
        return status_message
    except Exception as e:
        status_message = f"An unexpected error occurred during submission: {e}"
        print(status_message)
        return status_message
