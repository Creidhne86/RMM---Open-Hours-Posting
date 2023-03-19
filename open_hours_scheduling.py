import requests
import discord
import datetime
import pytz
import calendar
import asyncio

intents = discord.Intents.default()
intents.members = True  # Enable the members intent to access member-related events

client = discord.Client(intents=intents)


def generate_event_dates_for_month(year, month):
    event_dates = []
    first_day, days_in_month = calendar.monthrange(year, month)

    for day in range(1, days_in_month + 1):
        current_date = datetime.date(year, month, day)
        weekday = current_date.weekday()

        if weekday == calendar.TUESDAY or weekday == calendar.THURSDAY:
            event_dates.append(current_date)
        elif weekday == calendar.SUNDAY:
            event_dates.append(current_date)

    return event_dates


def create_event_for_date(date, time, duration):
    event_datetime = datetime.datetime.combine(date, time)
    cst_timezone = pytz.timezone("America/Chicago")
    cst_datetime = cst_timezone.localize(event_datetime)
    utc_datetime = cst_datetime.astimezone(pytz.utc)
    unix_timestamp = int(utc_datetime.timestamp())

    return {
        "date": unix_timestamp,
        "duration": duration,
    }


year, month = datetime.date.today().year, datetime.date.today().month + 1
event_dates = generate_event_dates_for_month(year, month)
tue_thu_time = datetime.time(hour=12, minute=0)
sunday_time = datetime.time(hour=11, minute=0)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    for date in event_dates:
        if date.weekday() == calendar.SUNDAY:
            time = sunday_time
            duration = 180
            day = "Sunday"
        else:
            time = tue_thu_time
            duration = 120
            day = "Tuesday" if date.weekday() == calendar.TUESDAY else "Thursday"

        event_data = create_event_for_date(date, time, duration)

        event = {
            "title": f"{day} Open Hours",
            "description": "",
            "templateId": 1,
            "date": event_data["date"],
            "leaderId": LEADER_ID,
            "advancedSettings": {"duration": event_data["duration"], "limit": 1},
        }

        print(f"Test event JSON data: {event}")

        post_data = {
            **event,
            "date": event["date"],
            "time": event["date"],
        }

        try:
            response = requests.post(
                f"https://raid-helper.dev/api/v2/servers/{SERVER_ID}/channels/{CHANNEL_ID}/event",
                headers={"Authorization": API_KEY, "Content-Type": "application/json; charset=utf-8"},
                json=post_data,
            )

            response.raise_for_status()
            print(f'Posted event "{event["title"]}"')
            print(response.text)  # Print the response body for debugging
        except requests.exceptions.RequestException as e:
            print(f"Error posting event: {e}")

        await asyncio.sleep(30)  # Wait for 30 seconds before posting the next event

# Log in to Discord
client.run(BOT_TOKEN)
