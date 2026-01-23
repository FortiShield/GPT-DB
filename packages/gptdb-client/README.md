# GPT-DB Client

`gptdb-client` is the official Python client for **GPT-DB**. It provides a convenient way to interact with a GPT-DB server from your Python applications.

## ✨ Features

- **Easy-to-Use API**: A simple and intuitive API for interacting with GPT-DB.
- **Synchronous and Asynchronous Support**: Supports both sync and async programming.
- **Connection Management**: Handles connections to the GPT-DB server efficiently.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher

### Installation

To install the client, run the following command:

```bash
pip install gptdb-client
```

### Usage

Here's a simple example of how to use the client:

```python
from gptdb_client import Client

# Connect to the GPT-DB server
client = Client(host="localhost", port=8000)

# Example: Send a query
response = client.query("What is the capital of France?")
print(response)
```

## 🤝 Contributing

Contributions are welcome! Please see the [contributing guidelines](../../CONTRIBUTING.md) for more information.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.
