import streamlit as st
import os
import google.generativeai as genai
import wordninja


st.title("Resume Chat Bot using Gemini")
message = ''
data = []
# Set Google API key
os.environ['GOOGLE_API_KEY'] = "AIzaSyDA4jQSg9sUH57Glynkt9RsXKU5QDx1j6I"
genai.configure(api_key = os.environ['GOOGLE_API_KEY'])
generation_config = {
"temperature": 0.9,
"top_p": 1,
"top_k": 1,
"max_output_tokens": 2048,
}

safety_settings = [
{
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_ONLY_HIGH"
},
{
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_ONLY_HIGH"
},
{
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_ONLY_HIGH"
},
{
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_ONLY_HIGH"
}
]

model = genai.GenerativeModel(model_name="gemini-pro",
                            generation_config=generation_config,
                            safety_settings=safety_settings)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role":"assistant",
            "content":"Enter Your Resume:"
        }
    ]


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Process and store Query and Response
def llm_function(query):
    size = len(st.session_state.messages)
    if size <12:      #   The number of Q/A after which the analysis or report is given 12/2 = 6
        if size == 1:
            query = f"""You are an interviewer for an MBA college admission panel. Here is the information of the candidate:
            {query}
    As the interviewer please ask a question that focuses on his qualifications."""
        elif size > 1 and size <=11:
            query = query + ".Please ask the next question."
        convo = model.start_chat(history=data)
        convo.send_message(query)
        results = []
        sentences = convo.last.text.split('.')
        for sentence in sentences:
    # Split each sentence into words using wordninja
            words = wordninja.split(sentence)
            
            # Join the words back together
            reconstructed_sentence = ' '.join(words)
            results.append(reconstructed_sentence)

        result = '. '.join(results)
        # Displaying the Assistant Message
        with st.chat_message("assistant"):
            st.markdown(result)

        data.append({"role": "user","parts": query})


        # Storing the User Message
        st.session_state.messages.append(
            {
                "role":"user",
                "content": query
            }
        )
        data.append({"role": "model","parts": result})
        # Storing the User Message
        st.session_state.messages.append(
            {
                "role":"assistant",
                "content": result
            }
        )
    else:
        message = ''
        for i in range(1,len(data)):
            now = data[i]['parts'] + '\n'
            message = message + now
        prompt_parts = [
f"Here is an exchange between interviewer and candidate. Based on his question and answers evaluate his performance:  {message}"
]

        response = model.generate_content(prompt_parts)
        with st.chat_message("assistant"):
                st.markdown(response.text)

        data.append({"role": "user","parts": query})


            # Storing the User Message
        st.session_state.messages.append(
            {
                "role":"user",
                "content": query
            }
        )

        data.append({"role": "model","parts": response})
        # Storing the User Message
        st.session_state.messages.append(
            {
                "role":"assistant",
                "content": response.text
            }
        )


# Accept user input
query = st.chat_input("Answer")


# Calling the Function when Input is Provided
if query:
    # Displaying the User Message
    with st.chat_message("user"):
        st.markdown(query)
    messages = st.session_state.messages
    for i in range(1,len(st.session_state.messages)):
        if i%2 == 0:
            message = messages[i]
            data.append({"role": "model","parts": message['content']})
        else:
            message = messages[i]
            data.append({"role": "user","parts": message['content']})

    llm_function(query)
