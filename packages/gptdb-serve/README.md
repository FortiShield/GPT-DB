# GPT-DB Serve

`gptdb-serve` is a sub-package of **GPT-DB** that provides serving capabilities for the system. It allows you to expose your GPT-DB functionalities as a service, making it accessible to other applications and services.

## ✨ Features

- **Expose GPT-DB as a Service**: Easily serve your GPT-DB instance over the network.
- **Scalable and Performant**: Built to handle multiple requests efficiently.
- **Easy Integration**: Simple to integrate with your existing infrastructure.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- GPT-DB installed

### Installation

To install the necessary dependencies, run the following command:

```bash
pip install -r requirements.txt
```

### Usage

To start the server, use the following command:

```bash
python -m gptdb_serve.app
```

This will start the server on `localhost` at port `8000` by default. You can configure the host and port by setting the `HOST` and `PORT` environment variables.

## 🤝 Contributing

Contributions are welcome! Please see the [contributing guidelines](../../CONTRIBUTING.md) for more information.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.
