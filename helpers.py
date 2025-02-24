from mistral_common.protocol.instruct.request import ChatCompletionRequest
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from mistral_common.protocol.instruct.messages import UserMessage


model_name = "mistralai/Mistral-NeMo-Instruct-2407"
tokenizer = MistralTokenizer.from_model(model_name)

def read_spreadsheet(html_file):
    with open(html_file, 'r') as f:
        html_content = f.read()

    return html_content


def tokeniser_check(prompt):
    tokenized = tokenizer.encode_chat_completion(
        ChatCompletionRequest(messages=[UserMessage(content=prompt)])
    )
    # print(tokenized.tokens, tokenized.text)
    return len(tokenized.tokens) <= 199000
