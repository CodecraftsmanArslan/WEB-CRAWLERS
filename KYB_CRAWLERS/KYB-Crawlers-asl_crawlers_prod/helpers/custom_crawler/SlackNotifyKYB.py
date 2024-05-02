"""Import required libraries"""
import json
import requests

class SlackNotifier:
    def __init__(self, crawler_name: str, ENV:dict):
        self.crawler_name = crawler_name
        self.ENVIRONMENT = ENV['ENVIRONMENT']
        self.CHANNEL_NAME = ENV["SLACK_CHANNEL_NAME"]
        self.WARNINGS_CHANNEL_NAME = ENV["WARNINGS_CHANNEL_NAME"]
        self.PLATFORM  = ENV['PLATFORM']
        self.SERVER_IP = ENV['SERVER_IP']
        self.SLACK_WEB_HOOK = ENV['SLACK_WEB_HOOK']
        self.WARNINGS_WEB_HOOK = ENV['WARNINGS_WEB_HOOK']


    def slack_notification_content(self, data, crawler_name):
        """
        Prepare the content for Slack notification based on the event type.
        @param data (dict): The notification data.
        @param crawler_name (str): The name of the crawler.
        @return dict: The formatted Slack notification data.
        """
        content = data["message"]
        crawler_name_text = f"*Crawler Name: * {crawler_name}"
        
        if data["event"] == "fail":
            message = (
                f"*Type: * {content['source_type']}\n"
                f"*URL/Path: * {content['source_url']}\n"
                f"*Message: * {content['error_message']}\n"
                f"*Status: * {content['status']}\n"
                f"*Number of records Inserted: * {content['num_records']}\n"
            )
            title = "Error"
            color = "#FF0000"
        else:
            message = content
            title = "Notifications from crawler"
            color = "#0000FF"

        slack_data = {
            "channel": self.CHANNEL_NAME if data["event"] == "success" else self.WARNINGS_CHANNEL_NAME,
            "attachments": [
                {
                    "color": color if message.find('has been completed successfully')==-1 else '#4BB543',
                    "fields": [
                        {
                            "title": title,
                            "value": (
                                f"*Platform: * {self.PLATFORM}\n"
                                f"*SERVER: * {self.SERVER_IP}\n"
                                f"{crawler_name_text}\n"
                                f"{message}\n"
                            ),
                            "short": "false",
                        }
                    ]
                }
            ]
        }
        return slack_data

    def notify(self, data):
        """
        Send a Slack notification.
        @param data (dict): The notification data.
        """
        if self.ENVIRONMENT != 'LOCAL':
            slack_data = self.slack_notification_content(data, self.crawler_name)
            headers = {'Content-Type': "application/json"}
            requests.post(
                self.SLACK_WEB_HOOK if data["event"] == "success" else self.WARNINGS_WEB_HOOK,
                data=json.dumps(slack_data),
                headers=headers
            )
    
    def crawler_start(self):
        """
        Notify the start of the crawler.
        """
        data = {
            "event": "start",
            "message": f"Data crawling has been started for {self.crawler_name}"
        }
        self.notify(data)

    def crawler_completed(self, num_records):
        """
        Notify the end of the crawler.
        """
        data = {
            "event": "end",
            "message": f"Data crawling for {self.crawler_name} has been completed successfully\n"
                       f"*Number of Records Inserted: * {num_records}"
        }
        self.notify(data)
