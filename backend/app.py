import json

def read_json_file(filename):
  """Reads a JSON file and returns the contents as a Python dictionary.

  Args:
    filename: The name of the JSON file to read.

  Returns:
    A Python dictionary containing the contents of the JSON file.
  """

  with open(filename, "r") as f:
    data = json.load(f)

  return data

# Example usage:

data = read_json_file("data.json")
# print(data)

def objects_to_paragraphs(objects):
  """Converts an array of objects to an array of paragraphs.

  Args:
    objects: An array of objects.

  Returns:
    An array of paragraphs.
  """

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
index = "travel-chatbot" # pinecone index 

# embeddings = []
# for text in res:
#     embedding = pinecone.embed(text)
#     embeddings.append(embedding)

docsearch = Pinecone.from_texts(res, embeddings, index_name=index)

# Print a success message
# print("Data successfully embedded in Pinecone DB!")

from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain

query = "Tell me about place with id 1?"
llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
chain = load_qa_chain(llm, chain_type="stuff")
docs = docsearch.similarity_search(query)
answer = chain.run(input_documents=docs, question=query)

print(answer)