from mistral_common.protocol.instruct.request import ChatCompletionRequest
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from mistral_common.protocol.instruct.messages import UserMessage

from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.docstore.document import Document

from typing import Dict, List, Any
from openai import OpenAI

MODEL_NAME: str = "mistralai/Mistral-Nemo-Instruct-2407"
tokenizer: MistralTokenizer = MistralTokenizer.from_model(MODEL_NAME)

SYSTEM_PROMPT: str = """ You are a helpful assistant for question answering based on spreadsheets.
You always answer in 2-3 sentences.
"""

def init_inference_client() -> OpenAI:
    """Initializes and returns an OpenAI client wrapper for local inference instance."""
    inference_client: OpenAI = OpenAI(
        api_key="NOT REQUIRED",
        base_url="http://localhost:8000/v1"
    )
    return inference_client

def tokeniser_check(prompt: str) -> bool:
    """Checks if the tokenized prompt is within the allowed model context window limit."""
    tokenized = tokenizer.encode_chat_completion(
        ChatCompletionRequest(messages=[UserMessage(content=prompt)])
    )
    return len(tokenized.tokens) <= 128000

def refine_qa(spreadsheet_slices: List[str], headers: List[List[str]], question: str) -> Dict[str, Any]:
    """Runs Refine Chain on sliced spreadsheet to improve answer factuality."""
    slices = [Document(page_content=slice_text) for slice_text in spreadsheet_slices]

    llm = ChatOpenAI(
        api_key="NOT REQUIRED",
        model_name="mistralai/Mistral-Nemo-Instruct-2407",
        base_url="http://localhost:8000/v1",
        max_tokens=512,
    )

    row_h = " ".join(headers[0])
    col_h = " ".join(headers[1])

    init_prompt_template = (
        f"You are given a spreadsheet with the following row headers: {row_h} and column headers: {col_h}.\n"
        "Here is the spreadsheet exported as html: <spreadsheet>{text}</spreadsheet>\n"
        f"Using the information in the spreadsheet, answer the following question: {question}\n"
        "ANSWER:"
    )
    prompt = PromptTemplate.from_template(init_prompt_template)

    refine_template = (
        f"Your job is to answer the question: {question}\n"
        "Here's your first answer: {existing_answer}\n"
        "Now we have additional data from the spreadsheet:\n"
        "------------\n"
        "{text}\n"
        "------------\n"
        "Based on this new context, refine your answer. If the new data does not affect your answer, return the original answer."
    )
    refine_prompt = PromptTemplate.from_template(refine_template)

    chain = load_summarize_chain(
        llm=llm,
        chain_type="refine",
        question_prompt=prompt,
        refine_prompt=refine_prompt,
        return_intermediate_steps=True,
        input_key="input_documents",
        output_key="output_text",
    )

    result = chain({"input_documents": slices}, return_only_outputs=True)
    return result
