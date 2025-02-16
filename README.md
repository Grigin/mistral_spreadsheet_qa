# Hey 👋🏻

This repository contains code for an exploration of using Mistral open-source models inferenced locally using vLLM for QA on Spreadsheets.

## Repository Structure

It consists of three parts:

- **`app.py`** - Script that runs the GUI app.
- **`mistral_inference.py`** - All the inference-side functions are here.
- **`html_imaging_functions.py`** - All the logic for processing spreadsheets and extracting data from them.

## Getting Started

If you want to have a go at running the app, please follow these steps:

# 1️⃣ Setup

### Set up Miniconda:

#### On Linux:

```shell
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
```

#### On Mac:

##### M-series:
```shell
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -O ~/miniconda.sh
```

##### Intel:
```shell
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O ~/miniconda.sh
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