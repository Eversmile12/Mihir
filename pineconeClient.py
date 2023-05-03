import itertools
import pinecone
import os


class PineconeClient:
    def __init__(self):
        api_key = os.environ["PINECONE"]
        if api_key is None:
            raise ValueError(
                "Pinecone API key not found in environment variables")
        pinecone.init(api_key, environment="us-west1-gcp-free")

    def create_index(self, index_name):
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                index_name, dimension=1536, metric="cosine")

    def chunks(_, iterable, batch_size=100):
        """A helper function to break an iterable into chunks of size batch_size."""
        it = iter(iterable)
        chunk = tuple(itertools.islice(it, batch_size))
        while chunk:
            yield chunk
            chunk = tuple(itertools.islice(it, batch_size))

    # def check_index_present(index_name):
    #     active_indexes = pinecone.list_indexes()
    #     if index_name in active_indexes:
    #         return True
    #     else:
    #         return False

    def upsert_in_chunks(self, index_name, ids_vectors):
        # Upsert data with 100 vectors per upsert request
        responses = []
        print(ids_vectors)
        for ids_vectors_chunk in self.chunks(ids_vectors):
            upsert_response = pinecone.Index(
                index_name).upsert(vectors=ids_vectors_chunk)
            if upsert_response:
                responses.append(upsert_response)

        return responses

    def upsert_standard(self, index_name, ids_vectors):
        upsert_response = pinecone.Index(index_name).upsert(
            vectors=ids_vectors)
        return upsert_response

    def upsert(self, index_name, ids_vectors):
        if len(ids_vectors) >= 100:
            print("data too big, dividing in chunks")
            upsert_response = self.upsert_in_chunks(index_name, ids_vectors)
        else:
            print("upserting data without chunking")

            upsert_response = self.upsert_standard(index_name, ids_vectors)
        return upsert_response

    def query(_, index_name, vector):
        index = pinecone.Index(index_name)
        top_neighbours = index.query(
            top_k=3,
            include_metadata=True,
            vector=vector,
        )
        if not top_neighbours:
            raise ValueError("No neighbors found")

        return top_neighbours["matches"]
