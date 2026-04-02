

import streamlit as st
import json
import os
from groq import Groq


client = Groq(api_key="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")

# 📁 Load customers
def load_customers():
    return [f.replace(".json", "") for f in os.listdir("customers")]

def get_context(customer_name):
    with open(f"customers/{customer_name}.json", "r") as f:
        return json.load(f)

# LLM call
def analyze_issue(ticket, logs, context):
    prompt = f"""
You are a technical support engineer for a data backup and security platform.

Use the customer context below to provide precise troubleshooting.

Customer Context:
{json.dumps(context, indent=2)}

Customer Ticket:
{ticket}

Logs:
{logs}

Return clearly:
1. Issue Summary
2. Root Cause (based on context)
3. Severity (Low/Medium/High)
4. Troubleshooting Steps (specific to environment)
5. Customer Response
6. Internal KB Note
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an expert technical support engineer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


#  Example scenarios
examples = {
    "IAM Permission Issue": {
        "ticket": "Backup failed for patient data. Access denied error while writing to storage.",
        "logs": "Error: AccessDenied: User is not authorized to perform s3:PutObject"
    },
    "Network Timeout": {
        "ticket": "Backup failed due to timeout while connecting to storage.",
        "logs": "Error: Connection timeout to 10.20.4.15:443"
    },
    "Disk Full": {
        "ticket": "Backup failed due to insufficient storage.",
        "logs": "Error: No space left on device"
    }
}


# UI
st.set_page_config(page_title="GenAI Support Assistant", layout="wide")

st.title("🧠 AI Support Assistant")
st.write("Analyze customer issues with AI using environment-specific context.")

# Customer selection
customers = load_customers()
selected_customer = st.selectbox("🏢 Select Customer", customers)

# Example selector
selected_example = st.selectbox("💡 Try an Example (for first-time users)", ["None"] + list(examples.keys()))

# Default / Example loading
if selected_example != "None":
    default_ticket = examples[selected_example]["ticket"]
    default_logs = examples[selected_example]["logs"]
else:
    default_ticket = ""
    default_logs = ""

#  Inputs
ticket_input = st.text_area(
    "🎫 Customer Issue",
    value=default_ticket,
    placeholder="Example: Backup failed for patient data due to access denied...",
    height=150
)

logs_input = st.text_area(
    "📜 Logs",
    value=default_logs,
    placeholder="Paste logs here (e.g., connection timeout, permission error...)",
    height=250
)

# 🔍 Analyze button
if st.button("🚀 Analyze Issue"):
    if ticket_input.strip() and logs_input.strip():
        context = get_context(selected_customer)

        with st.spinner("Analyzing with GenAI..."):
            result = analyze_issue(ticket_input, logs_input, context)

        st.subheader("✅ Analysis Result")
        st.write(result)

    else:
        st.warning("⚠️ Please enter both ticket and logs or select an example.")

