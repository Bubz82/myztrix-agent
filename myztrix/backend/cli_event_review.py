from gmail_agent import GmailAgent, add_event_to_calendar

CREDENTIALS_PATH = "../Config/credentials.json"
TOKEN_PATH = "../credentials/token.json"

def show_events(events):
    print("\n📬 Pending Event Suggestions:\n")
    for idx, event in enumerate(events):
        print(f"{idx+1}. {event.get('title', 'Untitled Event')}")
        print(f"   📅 Start: {event.get('start_time', 'Unknown')}")
        print(f"   🕒 End: {event.get('end_time', 'Unknown')}")
        snippet = event.get('description', '')
        print(f"   ✉️ Snippet: {snippet[:100]}...\n")

def review_events(events, agent):
    accepted = []
    for idx, event in enumerate(events):
        print(f"\n🔹 Event {idx+1}: {event.get('title', 'No Title')}")
        print(f"   Start: {event.get('start_time', 'Unknown')}")
        print(f"   End: {event.get('end_time', 'Unknown')}")
        decision = input("💭 Accept this event? (y/n): ").strip().lower()
        if decision == "y":
            accepted.append(event)
        else:
            # Optionally, mark declined with a label here or skip
            pass
    return accepted

def process_events():
    print("🔍 Authenticating and scraping Gmail for event candidates...")
    agent = GmailAgent(CREDENTIALS_PATH, TOKEN_PATH)
    if not agent.authenticate():
        print("❌ Authentication failed. Check your credentials and token.")
        return

    emails = agent.get_unread_emails()
    if not emails:
        print("📭 No unread emails found.")
        return

    events = []
    for email in emails:
        is_event, confidence, event_details = agent.detect_event(email)
        if is_event and event_details:
            events.append(event_details)

    if not events:
        print("🕵️‍♀️ No event candidates detected.")
        return

    show_events(events)
    accepted_events = review_events(events, agent)

    for event in accepted_events:
        print(f"\n📆 Adding to Google Calendar: {event.get('title')}")
        success = add_event_to_calendar(event)
        if success:
            agent.mark_as_read(event['email_id'])
            agent.add_label(event['email_id'], "CalendarAdded")
            print("✅ Event added and email marked.")
        else:
            print("⚠️ Failed to add event.")

if __name__ == "__main__":
    process_events()
