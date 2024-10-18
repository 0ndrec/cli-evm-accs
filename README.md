## Description
A simple CLI tool for safety managing EVM accounts.

![alt text](https://github.com/0ndrec/cli-evm-accs/blob/main/img.gif)

## 🚀 Setup

1. **Clone the repository**:
    ```sh
    git clone https://github.com/0ndrec/cli-evm-accs.git
    cd cli-evm-accs
    ```
    ```sh
    cp .env.example .env
    ```

2. **Install the required dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Configure your env and API keys in `.env`.**
   ```sh
   nano .env
   # DEFINE ENDPOINT
   ```
**⚠️ Important. The file keys.json stores encrypted keys. And the encryption token itself is in the file .env ⚠️**
** Please note that the application places .env and keys.json in the directory where it is called. **

## Autoinstall

```sh
  curl -s https://raw.githubusercontent.com/0ndrec/cli-evm-accs/refs/heads/main/install.sh | sudo bash
```

## 🛠 Usage

Run the script:
```sh
python main.py
```

Happy testing! 🎉
