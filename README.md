# Hey 👋🏻

This repository contains code for an exploration of using Mistral open-source models inferenced locally using vLLM for QA on Spreadsheets.

## Repository Structure

It consists of three parts:

- **`app.py`** - Script that runs the app.
- **`model_interaction.py`** - Logic for OpenAI wrapper, RefineChain processing using Langchain and local tokenization.
- **`html_imaging_functions.py`** - All the logic for processing spreadsheets in HTML and extracting data from them.

## Getting Started

If you want to have a go at running the app, please follow these steps:

# 1️⃣ Setup & Installation

### Set up Miniconda:

#### On Linux:

```shell
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
```

### Install Miniconda

```shell
chmod +x ~/miniconda.sh
~/miniconda.sh
mkdir -p ~/miniconda3
bash ~/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda.sh
```

### Initialize Conda

```shell
~/miniconda3/bin/conda init
source ~/.bashrc
```

⚠️ **Please restart your shell before proceeding!**

### Create a Conda environment

```shell
conda create --name spreadsheets-qa python=3.11
conda activate spreadsheets-qa
pip install -r requirements.txt
```
# 2️⃣ Inference Server 

⚠️ **Please create a new tmux session for the next few steps**
```shell
tmux new -s "inference-server"
```
#### In your new tmux sesh:

### Activate the conda env
```shell
conda activate spreadsheets-qa
```

### Authenticate on the HuggingFace Hub using your access token $HF_TOKEN:

```shell
huggingface-cli login --token $HF_TOKEN
```

### Start the inference server:

```shell
vllm serve mistralai/Mistral-Nemo-Instruct-2407 \
  --tokenizer_mode mistral \
  --config_format mistral \
  --load_format mistral
```

#### When the vllm server fires up at 0.0.0.0:8000
#### Exit tmux session:
`Ctrl` + `B` + `D`

# 3️⃣ Launch

### Run the app 
⚠️ **Please make sure that your conda env is activated**
```shell
python app.py
```

### Open the app using local link provided or temporal public link

# 4️⃣ How to use

#### 1. Select a spreadsheet to ask questions about from the three pre-uploaded (truncated) ones
+ Titanic https://www.kaggle.com/c/titanic/data (train.csv)
+ Wine Quality https://archive.ics.uci.edu/dataset/186/wine+quality?ref=hackernoon.com (winequality-red.csv)
+ Amazon Bestsellers data https://www.kaggle.com/datasets/sootersaalu/amazon-top-50-bestselling-books-2009-2019/ (bestsellers with categories.csv)

### OR

#### 1. Upload your own one (in .HTML format)
The spreadsheet parser only works with .html spreadsheets downloaded from Google Sheets.
To prepare your data in that way, please import your custom spreadsheet to Google Sheets.
Then go to: File -> Download -> Web page (.html)

#### You can play around with QA on spreadsheets using two modes (on two different tabs).
### Chat mode: 

The size of spreadsheet is limited (approx 450-500 rows max. because of the context window limitations) 
and the model tries to answer questions based on the whole spreadsheet. Faster and less factually precise.

### RefineChain mode:

No limitation on the size of the spreadsheet. Uses refine-chain approach to feed itself a spreadsheet splitted into chunks
of N rows (feel free to experiment with different chunk sizes) and with each new discovered chunk decides whether to alter the 
answer or stick to the current one.

#### 2. Type a question in the "Question" textbox
#### 3. Press "Submit" button
#### 4. Have fun =)







