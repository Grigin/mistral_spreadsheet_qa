import gradio as gr
from typing import Optional, Tuple, AsyncGenerator, List

from model_interaction import tokeniser_check, refine_qa, init_inference_client, SYSTEM_PROMPT, MODEL_NAME
from html_imaging_functions import spreadsheet_splitter, extract_headers, html_processor

client = init_inference_client()

SENSITIVE: bool = False  # Set this to true if you don't want gradio to save user logs automatically


def read_spreadsheet(html_file: str) -> str:
    """Reads an HTML file and returns its content as a string."""
    with open(html_file, 'r') as f:
        html_content = f.read()

    return html_content


def prepare_spreadsheet_data(selected_spreadsheet: str, uploaded_file: Optional[str] = None) -> Tuple[
    Optional[str], Optional[str]]:
    """Prepares spreadsheet data and returns a tuple of (table_html, error message)."""
    if selected_spreadsheet == "My Own":
        if uploaded_file is None:
            return None, "Please upload a file."
        try:
            with open(uploaded_file, 'r') as file:
                uploaded_html = file.read()
            table_html = html_processor(uploaded_html)
        except Exception as e:
            error_msg = (f"Ooops, the structure of your spreadsheet is unfamiliar to our parser machine. "
                         f"Sorry! \n {e}")
            return None, error_msg

    elif selected_spreadsheet == "Titanic":
        orig_html = read_spreadsheet('data/html/titanic_truncated.html')
        table_html = html_processor(orig_html)

    elif selected_spreadsheet == "Red Wine Data":
        orig_html = read_spreadsheet('data/html/winequality-red_truncated.html')
        table_html = html_processor(orig_html)

    elif selected_spreadsheet == "Bestsellers":
        orig_html = read_spreadsheet('data/html/bestsellers.html')
        table_html = html_processor(orig_html)

    else:
        return None, "Invalid spreadsheet selection."

    return table_html, None


async def refine_handler(selected_spreadsheet: str, step: int, message: str, uploaded_file: Optional[str] = None) -> \
AsyncGenerator[Tuple[str, str], None]:
    """Processes the spreadsheet data, refines the QA chain, and yields the final answer with its chain."""
    table_html, error = prepare_spreadsheet_data(selected_spreadsheet, uploaded_file)
    if error:
        yield error, error
        return

    slices = spreadsheet_splitter(table_html, int(step))
    rows, columns = extract_headers(table_html)
    spreadsheet_headers = [rows, columns]
    answers = refine_qa(slices, spreadsheet_headers, message)
    answer_chain = 'Here is the chain of answers: \n'
    for idx, answer in enumerate(answers.get('intermediate_steps')):
        answer_chain += f"\nAnswer {idx + 1}: \n {answer} \n"

    final_answer = answers.get('intermediate_steps')[-1]
    yield final_answer, answer_chain


async def chat_handler(selected_spreadsheet: str, message: str, uploaded_file: Optional[str] = None) -> AsyncGenerator[
    List[List[str]], None]:
    """Handles chat interactions by streaming answers based on the spreadsheet content."""
    table_html, error = prepare_spreadsheet_data(selected_spreadsheet, uploaded_file)
    if error:
        yield [["", error]]
        return

    user_prompt = (
        f"Here is a spreadsheet exported as html: <spreadsheet>{table_html}</spreadsheet>\n"
        f"Answer the following question about this spreadsheet (it's given to you in <spreadsheet></spreadsheet> tags):\n"
        f"{message}"
    )

    if not tokeniser_check(user_prompt):
        yield [["", "Spreadsheet is too big to be processed. Sorry!"]]
        return

    accumulated_response = ""
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=4096,
            stream=True,
        )
        for chunk in resp:
            delta = chunk.choices[0].delta.content
            accumulated_response += delta
            yield [[message, accumulated_response]]
    except Exception as e:
        yield [["", f"Error: {str(e)}"]]


spreadsheet_options: List[str] = ["Red Wine Data", "Titanic", "Bestsellers", "My Own"]

with gr.Blocks() as tabbed_demo:
    gr.Markdown('<h1>Spreadsheets QA Demo <sup>1.0</sup></h1>')
    gr.Markdown('<h3>Based on Mistral Nemo</h3>')
    log_flag = 'auto'
    if SENSITIVE:
        gr.Markdown(
            '<h4 style="color:red">This instance runs without logging and is safe for work with sensitive data</h4>')
        log_flag = 'never'
        print("Sensitive mode enabled")

    with gr.Tab("Chat with spreadsheet"):
        demo = gr.Interface(
            fn=chat_handler,
            inputs=[
                gr.Dropdown(spreadsheet_options, label="Spreadsheet",
                            info="Select a pre-loaded spreadsheet or upload your own"),
                gr.Textbox(placeholder="Question", type="text", label="Question"),
                gr.File(label="Upload Your Own (.html format only)", type="filepath", file_types=[".html"])
            ],
            outputs=gr.Chatbot(label="Answer"),
            theme="Monochrome",
            allow_flagging=log_flag
        ).queue()

    with gr.Tab("Refine-Chain QA"):
        demo = gr.Interface(
            fn=refine_handler,
            inputs=[
                gr.Dropdown(spreadsheet_options, label="Spreadsheet",
                            info="Select a pre-loaded spreadsheet or upload your own"),
                gr.Slider(minimum=10, maximum=50, step=5, value=10, label='Chunking step',
                          info="**HINT: 10 <= Precision | Speed => 50"),
                gr.Textbox(placeholder="Question", type="text", label='Question'),
                gr.File(label="Upload Your Own (.html format only)", type="filepath", file_types=[".html"])
            ],
            outputs=[gr.Textbox(label="Answer", type="text", show_copy_button=True),
                     gr.Textbox(label="Full Chain", type="text", show_copy_button=True)],
            theme="soft",
            allow_flagging=log_flag
        ).queue()

if __name__ == '__main__':
    tabbed_demo.launch(share=True)
