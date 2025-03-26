import streamlit as st
import json
#import assemblyai as aai
import os
from langchain_groq import ChatGroq

# Set API keys

GROQ_API_KEY = "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"

# Initialize ChatGroq model
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=GROQ_API_KEY
)

def translate_text(file_path):
    """translate it into English."""
    # if not os.path.exists(file_path):
    #     return {"error": f"File not found: {file_path}"}
    
    

    messages = [
        ("system", "Translate the following Hindi conversation into English while preserving speaker labels."),
        ("human", file_path),
    ]
    
    ai_translation = llm.invoke(messages).content

    return ai_translation

def classify_speakers(conversation_text):
    """Classify Client and Agent, rate the agent, and analyze responses."""
    messages = [
        ("system",
        "You are an AI that classifies speakers in a conversation as either 'Client' or 'Agent'.\n"
        "A Client asks for information or makes requests, while an Agent provides answers or handles requests.\n"
        "Additionally, provide:\n"
        "- An **Agent rating** out of 10 based on professionalism, clarity, and engagement.\n"
        "- An **analysis breakdown** of the Agent's behavior for each sentence.\n"
        "- The **factors used for rating** (such as politeness, accuracy, efficiency, etc.).\n"
        "- A detailed **Agent behavior breakdown**, mapping each client statement to the respective agent response and its evaluation.\n"
        "### JSON Output Format:\n"
        "{\n"
        '  "classification": {"agent": "Speaker A", "client": "Speaker B"},\n'
        '  "rating": 8,\n'
        '  "analysis": [\n'
        '    {"category": "Introduction", "description": "Professional greeting"},\n'
        '    {"category": "Verification", "description": "Clear and concise"}\n'
        '  ],\n'
        '  "rating_factors": ["Professionalism", "Clarity", "Politeness"],\n'
        '  "agent_behavior": [\n'
        '    {"client_statement": "Client: I need help with my account.",\n'
        '     "agent_response": "Agent: Sure, I can assist you. What issue are you facing?",\n'
        '     "evaluation": "Helpful and professional"}\n'
        '  ]\n'
        "}"),
        ("human", conversation_text),
    ]
    
    ai_msg = llm.invoke(messages)
    try:
        json_start = ai_msg.content.find("{")
        json_end = ai_msg.content.rfind("}") + 1
        json_text = ai_msg.content[json_start:json_end].strip()
        structured_response = json.loads(json_text)
    except json.JSONDecodeError:
        structured_response = {"error": "AI response was not in valid JSON format. Please try again."}
    
    return structured_response

# Streamlit UI
st.title("🔹 Hindi Client-Agent Classification")
st.write("Upload a Hindi conversation text file and click Translate & Classify'.")

#uploaded_file = st.file_uploader("📤 Upload an audio file (MP3, WAV)", type=["mp3", "wav"])

user_text = st.text_area("Enter conversation text:")
st.write(f"```\n{user_text}\n```")       

if st.button("🚀 Translate & Classify"):
    if user_text:
                
        translated_text = translate_text(user_text)
        
        if "error" in translated_text:
            st.error(translated_text["error"])
        else:
                        
            st.subheader("🌍 Translated English Text:")
            st.write(f"```{translated_text}```")
            
            result = classify_speakers(translated_text)
            
            if "error" in result:
                st.error(result["error"])
            else:
                st.subheader("✅ Classification Result")
                st.write(f"🔹 **Agent:** {result['classification']['agent']}")
                st.write(f"🔹 **Client:** {result['classification']['client']}")
                st.write(f"⭐ **Agent Rating:** {result['rating']}/10")
                
                st.subheader("📊 Analysis Breakdown")
                for item in result["analysis"]:
                    st.write(f"- **{item['category']}**: {item['description']}")
                
                st.subheader("📌 Rating Factors")
                for factor in result["rating_factors"]:
                    st.write(f"- {factor}")
                
                st.subheader("🔍 Agent Behavior on Each Statement")
                for item in result["agent_behavior"]:
                    st.write(f"- **Client:** {item['client_statement']}")
                    st.write(f"  **Agent:** {item['agent_response']}")
                    st.write(f"  🏷 **Evaluation:** {item['evaluation']}")
                    st.write("---")
    else:
        st.warning("⚠️ Please upload an audio file before transcribing.")
