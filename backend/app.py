import json
import pinecone
from langchain.vectorstores import Pinecone

def read_json_file(filename):
  with open(filename, "r") as f:
    data = json.load(f)

  return data

data = read_json_file("data.json")
# print(data)

def objects_to_paragraphs(objects):
  paragraphs = []
  for object in objects:
    paragraph = ""
    for key, value in object.items():
      paragraph += f"{key}: {value}\n"

    paragraphs.append(paragraph)

  return paragraphs

res = objects_to_paragraphs(data)
# print(res)

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PORT = os.getenv('PORT')

import pinecone
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_API_ENV = os.getenv('PINECONE_API_ENV')

pinecone.init(
    api_key=PINECONE_API_KEY,  
    environment=PINECONE_API_ENV 
)

index = "travel-chatbot" 

docsearch = Pinecone.from_texts(res, embeddings, index_name=index)

from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import openai

app = Flask(__name__)

CORS(app, resources={r"/ask": {"origins": ["http://127.0.0.1:5500", "https://travel-buddy-ga201.netlify.app"]}})
CORS(app, resources={r"/chat": {"origins": ["http://127.0.0.1:5500", "https://travel-buddy-ga201.netlify.app"]}})

product_func = [
    {
        "name":"get_places_images",
        "description": "Get all the images of particular place",
        "parameters": {
            "type":"object",
            "properties": {
                "data" : {
                    "type" : "array",
                    "items" : {
                        "type":"object",
                        "properties" : {
                            "images" : {
                                "type" :"string",
                                "description" : "Places image, e.g. https://t3.ftcdn.net/jpg/01/30/86/06/240_F_130860698_oBQfdpO4kdQ6EnMtvnCn90fOrClUvBuZ.jpg"
                            },
                            "names" : {
                                "type" :"string",
                                "description" : "Places names, e.g. Goa, Agra, Shimla"
                            },
                            "places_to_watch" : {
                                "type" :"string",
                                "description" : "Places to watch, e.g. Baga beach, Agra fort, Mall road, Nubra Valley"
                            },
                            "weather" : {
                                "type" :"string",
                                "description" : "Places weather, e.g. cold, moderate, hot"
                            },
                            "place_type" : {
                                "type" :"string",
                                "description" : "Places type, e.g. Historical, Hill Station, Beach"
                            }
                        },
                    "required" : ["name", "images", "place_type", "places_to_watch", "weather"]
                    }
                }
            },
            "required":["data"]
        }
    }
]

@app.route('/ask', methods = ['GET', 'POST'])
def ask():
  try:
      # Get the query from the client side
      query = request.json['user_input']
      # print(query)

      # Initialize the OpenAI model
      llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)

      # Load the QA chain
      chain = load_qa_chain(llm, chain_type="stuff")

      # Perform a similarity search to get relevant documents
      docs = docsearch.similarity_search(query)

      # Run the query through the chain
      answer = chain.run(input_documents=docs, question=query)

      completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages = [{"role" : "user", "content" : f"""{docs}"""}],
        functions = product_func,
        function_call = "auto"
      )
      # print(completion)
      output = completion.choices[0].message
      # print(output)
      arguments = json.loads(output.function_call.arguments)

      # names = [item['names'] for item in arguments['data']]
      # places_to_watch = [item['places_to_watch'] for item in arguments['data']]
      # weather = [item['weather'] for item in arguments['data']]
      # place_type = [item['place_type'] for item in arguments['data']]
      # # print(arguments)
      # images = [item["images"] for item in arguments["data"]]
      # print(images)
      # # Return the answer as JSON response
      response = {
          'answer': answer
      }

      # if "images" in query.lower():
      #    response["images"] = images
      # elif "names" in query.lower():
      #    response["names"] = names
      # elif "places" in query.lower():
      #    response["names"] = names
      return jsonify(response)
  
  except Exception as e:
      return jsonify({'error': str(e)}), 500

# Global dictionary to store chat history
chat_history = {}

@app.route('/chat', methods=['GET','POST'])
def chat():
    user_input = request.json['user_input']
    # Generate a response from OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages= [{"role": "system", "content": "You are a helpful travel assistant, who help users with their travel, vacation, trip related queries only. If users ask questions other than travel related queries, you have to say Sorry, I am designed to help you in Travel related queries only."},
                   {"role" : "user", "content" : user_input}],
        temperature=0.7,  # Adjust as needed
        max_tokens=300,
        top_p=1,   # Adjust the response length
    )

    # Extract and save the chatbot's reply to the conversation history
    chatbot_reply = response['choices'][0]['message']['content']
    return jsonify({'response': chatbot_reply})

if __name__ == '__main__':
    app.run(port=PORT)




