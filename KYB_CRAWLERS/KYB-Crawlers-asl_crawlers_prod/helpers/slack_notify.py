"""Import required libraries"""
import os
import json
import requests

ENVIROMENT = os.getenv('ENVIROMENT')


class SlackNotifier:

    @staticmethod
    def slack_notification_content(data):
        content = data["message"]
        if data["event"] == "fail":
            message = f"*Type: * " + content["source_type"] + "\n" + \
                f"*URL/Path: * " + content["source_url"] + "\n" + f"*Message: * " + content["error_message"] + \
                      "\n" + f"*Status: * " + content["status"]
            title = f"Error"
            color = "#FF0000"
        elif data['event'] == "faulty":
            message = f"*Type: * " + content["source_type"] + "\n"\
                      + f"*URL/Path: * " + content["source_url"] + "\n" \
                      + f"*Message: * " + "Crawler Completed with Some Missing Keys" + "\n" \
                      + f"*Missing Keys: * {content['missing_keys']}" + "\n" \
                      + f"*Number of Records: * {content['num_records']}" + "\n" \
                      + f"*Status: * " + "Warning!"
            title = f"Missing Keys"
            color = "#FFA500"
        else:
            message = content
            title = "Notifications from crawler"
            color = "#0000FF"

        slack_data = {
            "channel": os.getenv("SLACK_CHANNEL_NAME") if data["event"] == "success" else os.getenv("WARNINGS_CHANNEL_NAME"),
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": title,
                            "value": f"*Platform: * " +
                            os.getenv('PLATFORM') + "\n" + f"*SERVER: * " +
                            os.getenv('SERVER_IP') + "\n" + message,
                            "short": "false",
                        }
                    ]
                }
            ]
        }
        return slack_data

    def notify(self, data):
        if ENVIROMENT != 'LOCAL':
            slack_data = self.slack_notification_content(data)
            headers = {
                'Content-Type': "application/json",
            }
            requests.post(os.getenv('SLACK_WEB_HOOK') if data["event"] == "success" else os.getenv(
                "WARNINGS_WEB_HOOK"), data=json.dumps(slack_data), headers=headers)
