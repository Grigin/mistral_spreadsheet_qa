import asyncio
import time
from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams
import torch
from vllm.inputs import TextPrompt
from mistral_common.protocol.instruct.request import ChatCompletionRequest
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from mistral_common.protocol.instruct.messages import UserMessage

MAX_RETRIES = 3
RETRY_DELAY = 20


inference_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model_name = "mistralai/Mistral-NeMo-Instruct-2407"
tokenizer = MistralTokenizer.from_model(model_name)
sampling_params = SamplingParams(max_tokens=512, temperature=0.9)

engine_args = AsyncEngineArgs(model=model_name, enforce_eager=True)
llm = AsyncLLMEngine.from_engine_args(engine_args)

def read_spreadsheet(html_file):
    with open(html_file, 'r') as f:
        html_content = f.read()

    return html_content

async def get_completion(prompt):
    print(f"Got prompt: {prompt}")
    retries = 0
    while retries < MAX_RETRIES:
        try:
            previous_text = ""
            request_id = time.monotonic()
            results_generator = llm.generate(prompt, sampling_params, request_id=request_id)
            async for request_output in results_generator:
                text = request_output.outputs[0].text
                new_chunk = text[len(previous_text):]
                previous_text = text
                yield new_chunk
            break
        except Exception as e:
            print(f"Generation failed: {e}")
            retries += 1
            if retries < MAX_RETRIES:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print("Max retries reached. Skipping this request.")
                break


def tokeniser_check(prompt):
    tokenized = tokenizer.encode_chat_completion(
        ChatCompletionRequest(messages=[UserMessage(content=prompt)])
    )
    # print(tokenized.tokens, tokenized.text)
    return len(tokenized.tokens) <= 199000

# Example usage
# async def main():
#     prompt = TextPrompt(prompt="Answer in 2-3 sentences: What are you?")
#     async for output in get_completion(prompt):
#          print("Final Model output:", output)

# if __name__ == '__main__':
#     asyncio.run(main())
