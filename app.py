import gradio as gr
from mistral_inference import get_completion, read_spreadsheet, tokeniser_check
from html_imaging_functions import html_processor

async def handler(selected_spreadsheet, message, uploaded_file):
    # Process the spreadsheet HTML based on selection
    if selected_spreadsheet == "My Own":
        if uploaded_file is not None:
            with open(uploaded_file, 'r') as file:
                uploaded_html = file.read()
                table_html = html_processor(uploaded_html)
        else:
            yield [["", "Please upload a file."]]
            return
    elif selected_spreadsheet == "Anecdotal 45x50":
        table_html = read_spreadsheet('data/html/meta.html')
    elif selected_spreadsheet == "Retrieval Pricing":
        orig_html = read_spreadsheet('data/html/retrieval.html')
        table_html = html_processor(orig_html)
    elif selected_spreadsheet == "Titanic Truncated":
        orig_html = read_spreadsheet('data/html/titanic_truncated.html')
        table_html = html_processor(orig_html)
    else:
        yield [["", "Invalid spreadsheet selection."]]
        return

    system_prompt = f"""Here is spreadsheet exported as html: <spreadsheet>{table_html}</spreadsheet>
Answer the following question about this spreadsheet (it's given to you in <spreadsheet></spreadsheet> tags):
{message}"""

    if not tokeniser_check(system_prompt):
        yield [["", "Spreadsheet is too big to be processed. Sorry!"]]
        return

    accumulated_response = ""
    async for partial_text in get_completion(system_prompt):
        accumulated_response += partial_text
        yield [["User: " + message, accumulated_response]]


spreadsheet_options = ["Spreadsheet 45x50", "Retrieval Pricing", "Titanic Truncated", "My Own"]

demo = gr.Interface(
    fn=handler,
    inputs=[
        gr.Dropdown(spreadsheet_options, label="Spreadsheet",
                    info="Select a pre-loaded spreadsheet or upload your own"),
        gr.Textbox(placeholder="Question", type="text", label='Question'),
        gr.File(label="Upload Your Own (.html format only)", type="filepath", file_types=["html"])
    ],
    outputs=gr.Chatbot(label="Response"),
    title="Spreadsheets QA Demo",
    description="Based on Mistral-NeMo-Instruct",
    theme="soft",
    allow_flagging='never'
).queue()

if __name__ == '__main__':
    demo.launch(share=True)

