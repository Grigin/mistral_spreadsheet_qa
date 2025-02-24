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
tmux new -s "inference-sever"
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







