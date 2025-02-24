import gradio as gr
from openai import OpenAI
from helpers import read_spreadsheet, tokeniser_check
from html_imaging_functions import html_processor

client = OpenAI(
    api_key="NOT REQUIRED",
    base_url="http://localhost:8000/v1"
)

async def handler(selected_spreadsheet, message, uploaded_file):
    if selected_spreadsheet == "My Own":
        if uploaded_file is not None:
            with open(uploaded_file, 'r') as file:
                uploaded_html = file.read()
            table_html = html_processor(uploaded_html)
        else:
            yield [["", "Please upload a file."]]
            return
    elif selected_spreadsheet == "Spreadsheet 45x50":
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

    system_prompt = f"""Here is a spreadsheet exported as html: <spreadsheet>{table_html}</spreadsheet>
Answer the following question about this spreadsheet (it's given to you in <spreadsheet></spreadsheet> tags):
{message}"""

    if not tokeniser_check(system_prompt):
        yield [["", "Spreadsheet is too big to be processed. Sorry!"]]
        return

    accumulated_response = ""
    try:
        resp = client.chat.completions.create(
            model="mistralai/Mistral-Small-Instruct-2409",
            messages=[{"role": "user", "content": system_prompt}],
            max_tokens=150,
            stream=True,
        )
        for chunk in resp:
            delta = chunk.choices[0].delta.content
            accumulated_response += delta
            yield [["User: " + message, accumulated_response]]
    except Exception as e:
        yield [["", f"Error: {str(e)}"]]

spreadsheet_options = ["Spreadsheet 45x50", "Retrieval Pricing", "Titanic Truncated", "My Own"]

demo = gr.Interface(
    fn=handler,
    inputs=[
        gr.Dropdown(spreadsheet_options, label="Spreadsheet",
                    info="Select a pre-loaded spreadsheet or upload your own"),
        gr.Textbox(placeholder="Question", type="text", label="Question"),
        gr.File(label="Upload Your Own (.html format only)", type="filepath", file_types=["html"])
    ],
    outputs=gr.Chatbot(label="Response"),
    title="Spreadsheets QA Demo",
    description="Based on Mistral-Small-Instruct",
    theme="soft",
    allow_flagging="never"
).queue()

if __name__ == '__main__':
    demo.launch(share=True)
