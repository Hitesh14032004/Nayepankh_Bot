import streamlit as st
import os
import time
import warnings
import logging

# Suppress the ScriptRunContext warning
logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

st.set_page_config(page_title="NayePankh Connect AI", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
    .main-header { font-size:2.2rem; color: #FF4B4B; font-weight: 700; text-align: center; margin-bottom: 5px; }
    .sub-header { font-size:1.1rem; text-align: center; color: #555; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>NayePankh Foundation Connect</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>AI-Powered Volunteer Onboarding & Donor Routing Assistant</div>", unsafe_allow_html=True)

st.sidebar.header("⚙️ Configuration")
api_mode = st.sidebar.selectbox("Select AI Mode", ["Demo Mode (No API Key Required)", "Live OpenAI Mode"])

openai_api_key = ""
if api_mode == "Live OpenAI Mode":
    openai_api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")
    if not openai_api_key:
        st.sidebar.warning("Please enter an API key to proceed in Live Mode.")

if st.sidebar.button("Clear Conversation History"):
    st.session_state.messages = []
    st.session_state.workflow_step = "greeting"
    st.session_state.volunteer_data = {}
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "workflow_step" not in st.session_state:
    st.session_state.workflow_step = "greeting"
if "volunteer_data" not in st.session_state:
    st.session_state.volunteer_data = {}

if len(st.session_state.messages) == 0:
    initial_greet = (
        "Hello! 🙏 Welcome to NayePankh Foundation's AI Assistant. "
        "I can help you **Volunteer** for our upcoming drives, guide you on how to **Donate**, "
        "or answer any questions about our mission to help the underprivileged. How can I assist you today?"
    )
    st.session_state.messages.append({"role": "assistant", "content": initial_greet})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def generate_ai_response(user_input):
    if api_mode == "Live OpenAI Mode" and openai_api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            system_prompt = (
                "You are an AI assistant for NayePankh Foundation, a non-profit NGO in India working "
                "for education, women empowerment, and community development. Be extremely warm, polite, and helpful. "
                "Encourage users to volunteer or donate. Keep responses concise."
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ API Error: {str(e)}. Switching to basic response fallback."
            
    input_lower = user_input.lower()
    if "donate" in input_lower or "money" in input_lower or "contribution" in input_lower:
        return (
            "Thank you for your generosity! ❤️ Your donations directly fund our education and meal distribution drives. "
            "You can make a secure contribution online by clicking our official link: **[nayepankh.org/donate](https://nayepankh.org)**. "
            "Would you like information on our active operations?"
        )
    elif "mission" in input_lower or "about" in input_lower or "what do you do" in input_lower:
        return (
            "NayePankh Foundation is one of the leading NGO networks dedicated to supporting underprivileged communities. "
            "Our primary focus areas include continuous educational support for children, health checkup camps, and emergency relief distribution."
        )
    else:
        return "I appreciate you reaching out! I'm here to guide you on volunteering or donation routes. Could you please clarify if you'd like to join our workforce or support us financially?"

if user_query := st.chat_input("Type your message here..."):
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    bot_response = ""
    
    if st.session_state.workflow_step == "greeting" and "volunteer" in user_query.lower():
        st.session_state.workflow_step = "collecting_name"
        bot_response = "That's wonderful! We'd love to have you onboard. Let's get you registered. First, what is your **Full Name**?"
        
    elif st.session_state.workflow_step == "collecting_name":
        st.session_state.volunteer_data["name"] = user_query
        st.session_state.workflow_step = "collecting_email"
        bot_response = f"Thank you, {user_query}! Next, what is your **Email Address** so we can send you onboarding documents?"
        
    elif st.session_state.workflow_step == "collecting_email":
        st.session_state.volunteer_data["email"] = user_query
        st.session_state.workflow_step = "collecting_skills"
        bot_response = "Got it. Finally, what skills can you bring to NayePankh? (e.g., Teaching, Content Writing, Event Management, Social Media)"
        
    elif st.session_state.workflow_step == "collecting_skills":
        st.session_state.volunteer_data["skills"] = user_query
        st.session_state.workflow_step = "final_onboard"
        
        bot_response = (
            f"🎉 **Registration Complete!**\n\n"
            f"Thank you for stepping up, **{st.session_state.volunteer_data['name']}**.\n"
            f"We have noted your interest in **{st.session_state.volunteer_data['skills']}**. "
            f"Our onboarding specialist will reach out to **{st.session_state.volunteer_data['email']}** within 48 hours.\n\n"
            f"Is there anything else I can assist you with?"
        )
        st.session_state.workflow_step = "greeting"
        
    else:
        with st.spinner("Thinking..."):
            bot_response = generate_ai_response(user_query)
            
    time.sleep(0.4)
    with st.chat_message("assistant"):
        st.markdown(bot_response)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
