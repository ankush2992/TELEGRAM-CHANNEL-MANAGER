# Personal Channel Management Bot

This is a Telegram bot for managing multiple channels at once.

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(You should create a `requirements.txt` file by running `pip freeze > requirements.txt`)*

3.  **Create a `.env` file** for your secret credentials. Copy the example below and fill in your own values.
    ```
    API_ID=...
    API_HASH=...
    BOT_TOKEN=...
    ```

4.  **Create a `config.json` file** to define your channel groups.
    ```json
    {
      "group-name-1": [-100... , -100...],
      "group-name-2": [-100... , -100...]
    }
    ```

5.  **Run the bot:**
    ```bash
    python your_bot_script.py
    ```