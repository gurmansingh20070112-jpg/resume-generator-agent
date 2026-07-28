import streamlit as st
import os
import time
import langchain
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from tavily import TavilyClient
import pytesseract as pyt
import numpy as np
from langchain.messages import SystemMessage, HumanMessage
from langchain.agents import create_agent
from PIL import Image


#===================front end==============
st.title("AI resume maker & job apply agent")
st.image("https://towardsdatascience.com/wp-content/uploads/2025/01/1s2dtl0h7aipYWHfKVC7cUA.jpg",  width = 300)

GOOGLE_API_KEY = st.sidebar.text_input("GOOGLE API KEY", type= 'password')
GROQ_API_KEY = st.sidebar.text_input("GROQ API KEY", type = 'password')
TAVILY_API_KEY = st.sidebar.text_input("TAVILY API KEY", type = 'password')

if not (GOOGLE_API_KEY) and not (GROQ_API_KEY)  and not (TAVILY_API_KEY):
  st.sidebar.warning("Pass API key")
  st.stop()
else:
  st.success("API KEYS LOADED ")


#=========================== MODEL AND AGENT CODE ======================
# tool 1
def search_latest_news_jobs(query):
  """this function helps to get
  latest news amd latest jobs
  related to user given query
  using tavily"""

  from tavily import TavilyClient
  client = TavilyClient(api_key = TAVILY_API_KEY)
  return client.search(query)


# step 4: module and agent creation
model1 = ChatGoogleGenerativeAI(
    model = "gemini-3.5-flash-lite",
    google_api_key = GOOGLE_API_KEY
)

model2 = ChatGroq(
    model = "qwen/qwen3.6-27b",
    api_key = GROQ_API_KEY
)

#=================================Agent with tool===============================
agent = create_agent(
    model = model1,      # can be model2 also
    tools = [search_latest_news_jobs]
)


# let's Generate prompt for resume using model

def prompt_generator():
  prompt = """you are a helpful AI Resume
  maker, i want you to use chain-of-thoughts
  and give detailed prompt for model
  where user want to generate resume
  for fresher or experienced one
  in HTML format, you have to give proper
  set of instructions, an make sure to keep
  design professional"""

  responce = model1.invoke(prompt)
  prompt_ans = responce.content[-1]['text']
  # print(prompt_ans)

  file_name = 'prompt.txt'
  with open(file_name, 'w') as f:
    f.write(prompt_ans)


prompt_generator()



# final_Agent
# tool 2
def prompt_reader():
  with open('prompt.txt', 'r') as f:
    prompt = f.read()
  return prompt

prompt = """I want complete Professional
resume with dynamic design using advanced CSS and JS
and must show user input details
System instructions: Only Give HTML code as output"""

final_prompt = prompt + prompt_reader()

#================== IMAGE UPLOADER ======================
#================== UPLOAD IMAGE =======================  

File = st.sidebar.file_uploader(
  "choose an image file",
  type=["jpeg","jpg","png","webpg"]
)


if File is not None:
  try:
    image = Image.open(File)


    st.sidebar.image(image, caption= "uploaded image",
                     use_container_width=True)


    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")


      base_name = os.path.splitext(File.name)[0]
      save_path = f"{base_name}.jpg"
      
      image.save(save_path, "JPEG")
      st.sidebar.success(f" IMAGE succesfully saved as  `{save_path}`!")

  except Exception as e:
    st.error(f"Error processing image: {e}")


#change this when required new resume by user, pass details

user_info = st.text_input("give your information: ")
user_photo = st.sidebar.file_uploader("Upload pic", type = 'image/jpeg')


user_query = f"""give resume for python developer.
    User details : {user_info}
    use user profile image from given {user_photo}"""

final_query = final_prompt + user_query

if st.button("Generate Resume"):
  with st.spinner("Agent creating Resume..."):
    responce = agent.invoke({'messages':[{'role':'user',"content":final_query}]})
    code = responce['messages'][-1].content[-1]['text']

    st.html(code, width="stretch", unsafe_allow_javascript=True)
