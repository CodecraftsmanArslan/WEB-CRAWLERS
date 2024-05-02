"""Import Required lirbrary"""
import psycopg2
import requests
import json, os
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(host=os.getenv("STAGING_HOST"), port=os.getenv("STAGING_PORT"),
                        user=os.getenv("STAGING_USER"), password=os.getenv("STAGING_PASSWORD"),
                        dbname=os.getenv("STAGING_DB"))
cur = conn.cursor()


def slack_notification_content(data_list):
    """
    Prepare the content for Slack notification based on the event type.
    @param data_list (list): List of notification data dictionaries.
    @return dict: The formatted Slack notification data.
    """
    attachments = []
    platform = os.getenv('PLATFORM')
    server = os.getenv('SERVER_IP')

    for data in data_list:
        content = data["message"]
        if data["event"] == "fail":
            message = (
                f"*Country Name: * {content['country_name']}\n"
                f"*Number of Records: * {content['number_records']}\n"
                f"*Synced: * {content['synced']}\n"
                f"*Not Synced: * {content['not_synced']}\n"
                f"*QA Approved: * {content['qa_approved']}\n"
                f"*QA Unapproved: * {content['qa_unapproved']}\n"
            )
            color = "#FF0000"  # Red color for failure notifications
        else:
            message = (
                f"*Country Name: * {content['country_name']}\n"
                f"*Number of Records: * {content['number_records']}\n"
                f"*Synced: * {content['synced']}\n"
                f"*Not Synced: * {content['not_synced']}\n"
                f"*QA Approved: * {content['qa_approved']}\n"
                f"*QA Unapproved: * {content['qa_unapproved']}\n"
            )
            color = "#00FF00"  # Green color for success notifications

        attachments.append(
            {
                "color": color,
                "fields": [
                    {
                        "title": "DB NAME STAGING:",
                        "value": f"{message}\n",
                        "short": "false",
                    }
                ]
            }
        )

    slack_data = {
        "channel": os.getenv("KYB_SLACK_CHANNEL_NAME"),
        "attachments": [
            {
                "color": attachments[0]["color"],
                "fields": [
                    {
                        "title": "DB NAME STAGING:",
                        "value": (
                            f"*Platform: * {platform}\n"
                            f"*SERVER: * {server}\n"
                            + "".join([attachment["fields"][0]["value"] for attachment in attachments])
                        ),
                        "short": "false",
                    }
                ]
            }
        ]
    }
    return slack_data


def notify(data_list):
    """
    Send a Slack notification.
    @param data_list (list): List of notification data dictionaries.
    """
    if os.getenv('ENVIRONMENT') != 'LOCAL':
        chunk_size = 14  # Number of notifications to send in each chunk
        chunks = [data_list[i:i+chunk_size] for i in range(0, len(data_list), chunk_size)]

        for chunk in chunks:
            slack_data = slack_notification_content(chunk)
            headers = {'Content-Type': "application/json"}
            requests.post(
                os.getenv('KYB_SLACK_WEB_HOOK'),
                data=json.dumps(slack_data),
                headers=headers
            )


query = """
        SELECT
        countries,
        COUNT(1) AS num_records,
        COUNT(CASE WHEN is_synced = true THEN 1 END) AS synced_count,
        COUNT(CASE WHEN is_synced = false THEN 1 END) AS not_synced_count,
        COUNT(CASE WHEN is_qa = true THEN 1 END) AS qa_count,
        COUNT(CASE WHEN is_qa = false THEN 1 END) AS not_qa_count
        FROM
        reports where categories::text = '["Official Registry"]'
        GROUP BY
        countries;
        """

cur.execute(query)
results = cur.fetchall()
print("Fatching data from database")
notification_data_list = []
for result in results:
    country_name = result[0]
    number_records = result[1]
    synced = result[2]
    not_synced = result[3]
    qa_approved = result[4]
    qa_unapproved = result[5]

    notification_data = {
        "event": "success",
        "message": {
            "country_name": country_name,
            "number_records": number_records,
            "synced": synced,
            "not_synced": not_synced,
            "qa_approved":qa_approved,
            "qa_unapproved": qa_unapproved
        }
    }
    notification_data_list.append(notification_data)

# Send Slack notification
notify(notification_data_list)