"""간단한 설정 관리"""
import yaml
import os
from dotenv import load_dotenv


class Config:
    def __init__(self, path: str = "config.yaml"):
        load_dotenv()  # Load environment variables from .env file

        with open(path, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)

        # Override slack tokens with environment variables if they exist
        if 'slack' not in self.data:
            self.data['slack'] = {}
        
        bot_token = os.getenv("SLACK_BOT_TOKEN")
        if bot_token:
            self.data['slack']['bot_token'] = bot_token
        
        app_token = os.getenv("SLACK_APP_TOKEN")
        if app_token:
            self.data['slack']['app_token'] = app_token

    def __getitem__(self, key):
        return self.data[key]
