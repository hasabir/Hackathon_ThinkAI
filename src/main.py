import itertools
import random
import csv
import requests
import pickle as pkl
import cohere
import pinecone
import numpy as np

api_key = "EAJrctVW8xYbVHEKuXvFaxmq2zIHPejqpqn6Z3Ae"
co = cohere.Client(api_key)

request_texte = input("what is your question: ")
def embed_request(request_text):
	response = co.embed(
	texts=[request_text],
	model='small',
	)
	return response

vec_request =  embed_request(request_texte)


rows = []
def embed_file(path):
	with open(path, 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			row_str = ' '.join(row)
			rows.append(row_str)
		responses = co.embed(
			texts=rows,
			model='small',
			)
	return responses
responses = embed_file('../only10rows.csv')

with open("cache/responses.pkl", "wb") as file:
    pkl.dump(responses, file)

with open("cache/responses.pkl", "rb") as file:
    responses = pkl.load(file)

array_file = np.array(responses.embeddings)

def calculate_similarity(a, b):
  return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
sim = [calculate_similarity(np.array(vec_request.embeddings),np.array(responses.embeddings)[i]) for i in range(len(responses))]

top = 1
top_idx = np.argsort(sim, 0)[::-1][:top]
answers_list = []
for j in top_idx:
    answers_list.append(rows[int(j[0])])


refs = '\n'.join(answers_list)
prompt = f""" 
You are a guid in high school how answers student's questions. Using the references below, answer the following query while citing the references:

Query:
{request_texte}

References:
{refs} 

Detailed answer (with explanations):

"""
print(prompt)
response = co.generate(  
    model='command-xlarge-nightly',  
    prompt = prompt,  
    max_tokens=512,  
    temperature=0.6,  
    )

resp = response.generations[0].text
print(resp)