import faiss
import os
import click
import numpy as np
from sentence_transformers import SentenceTransformer


model_label = 'all-MiniLM-L6-v2'


model = SentenceTransformer(model_label)


def update_central_ledger(key, path_of_embedding):
	try:
		central_ledger = os.path.join('data', 'central_ledger.txt')
		if not os.path.exists(central_ledger):
			with open(central_ledger, 'w') as f:
				f.write(f'{key} : {path_of_embedding}\n')
			return
		with open(central_ledger, 'a') as f:
			f.write(f'{key} {path_of_embedding}\n')
	except Exception as e:
		raise f"Error updating central ledger: {e}"



def store_embeddings(embeddings, path_of_embedding: str) -> tuple:
	try:
		dimension = embeddings.shape[1]
		index = faiss.IndexFlatL2(dimension)
		index.add(np.array(embeddings, dtype=np.float32))
		faiss.write_index(index, path_of_embedding)
	except Exception as e:
		raise f"Error storing embeddings: {e}"




def create_embedding(texts: list[str]):
	try:
		embeddings = model.encode(texts, show_progress_bar=True)
		click.secho(f'Embeddings created for {len(texts)} texts', fg='green')
		click.secho(f'Embedding size: {embeddings.shape}', fg='green')
		return embeddings
	except Exception as e:
		raise f"Error creating embeddings: {e}"


def embeddings_wrapper(texts: list[str], key, path_of_embedding: str):
	try:
		embeddings = create_embedding(texts)
		store_embeddings(embeddings, path_of_embedding)
		update_central_ledger(key, path_of_embedding)
	except Exception as e:
		click.secho(e, fg='red')
		raise e
