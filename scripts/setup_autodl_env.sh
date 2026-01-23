#!/bin/bash
# This script is used for setting up the environment required for GPT-DB on https://www.autodl.com/

# Usage: source /etc/network_turbo && curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/khulnasoft/GPT-DB/main/scripts/setup_autodl_env.sh | bash

# autodl usage: 
# conda activate gptdb
# cd /root/GPT-DB
# bash scripts/examples/load_examples.sh
# gptdb start webserver --port 6006

DEFAULT_PROXY="true"
USE_PROXY=$DEFAULT_PROXY

initialize_conda() {
    conda init bash
    eval "$(conda shell.bash hook)"
    source ~/.bashrc
    if [[ $USE_PROXY == "true" ]]; then 
        source /etc/network_turbo
        # unset http_proxy && unset https_proxy
    fi
}

setup_conda_environment() {
    conda create -n gptdb python=3.10 -y
    conda activate gptdb
}

install_sys_packages() {
    apt-get update -y && apt-get install git-lfs -y
}

clone_repositories() {
    cd /root && git clone https://github.com/khulnasoft/GPT-DB.git
    mkdir -p /root/GPT-DB/models && cd /root/GPT-DB/models
    git clone https://www.modelscope.cn/Jerry0/text2vec-large-chinese.git
    git clone https://www.modelscope.cn/qwen/Qwen2-0.5B-Instruct.git
    rm -rf /root/GPT-DB/models/text2vec-large-chinese/.git
    rm -rf /root/GPT-DB/models/Qwen2-0.5B-Instruct/.git
}

install_gptdb_packages() {
    conda activate gptdb && cd /root/GPT-DB && pip install -e ".[default]" && pip install transformers_stream_generator einops
    cp .env.template .env && sed -i 's/LLM_MODEL=glm-4-9b-chat/LLM_MODEL=qwen2-0.5b-instruct/' .env
}

clean_up() {
    rm -rf `pip cache dir`
    apt-get clean
    rm -f ~/.bash_history
    history -c
}

clean_local_data() {
    rm -rf /root/GPT-DB/pilot/data
    rm -rf /root/GPT-DB/pilot/message
    rm -f /root/GPT-DB/logs/*
    rm -f /root/GPT-DB/logsDbChatOutputParser.log
    rm -rf /root/GPT-DB/pilot/meta_data/alembic/versions/*
    rm -rf /root/GPT-DB/pilot/meta_data/*.db
}

usage() {
    echo "USAGE: $0 [--use-proxy]"
    echo "  [--use-proxy] Use proxy settings (Optional)"
    echo "  [-h|--help] Usage message"
}

# Command line arguments parsing
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --use-proxy)
        USE_PROXY="true"
        shift
        ;;
        -h|--help)
        help="true"
        shift
        ;;
        *)
        usage
        exit 1
        ;;
    esac
done

if [[ $help ]]; then
    usage
    exit 0
fi

# Main execution

if [[ $USE_PROXY == "true" ]]; then
    echo "Using proxy settings..."
    source /etc/network_turbo
fi

initialize_conda
setup_conda_environment
install_sys_packages
clone_repositories
install_gptdb_packages
clean_up
