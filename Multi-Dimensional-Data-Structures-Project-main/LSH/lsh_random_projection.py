import numpy as np
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix

# Function to read 'education' data from CSV
def read_education_data_from_csv(file_path):
    education_data = []
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            education = row["Education"]
            education_data.append(education)
    return education_data

# Read the 'education' data from the csv file
csv_file_path = r"Data\Tasting_LSH.csv"
education_data = read_education_data_from_csv(csv_file_path)

vectorizer = TfidfVectorizer()
tf_idf = csr_matrix(vectorizer.fit_transform(education_data))

# LSH Implementation
num_planes = 2  # Number of random hyperplanes
hash_tables = []
random_vectors_list = []  # Store random_vectors for each hash table

# Create multiple hash tables (for better results)
num_hash_tables = 6

for _ in range(num_hash_tables):
    # Generate random planes separately for each hash table
    random_vectors = np.random.randn(num_planes, tf_idf.shape[1])
    random_vectors_list.append(random_vectors)
    hash_table = {}
    hash_tables.append(hash_table)

    # Hash documents into buckets
    for i, doc in enumerate(tf_idf):
        projections = np.dot(doc.toarray(), random_vectors.T)
        hash_value = tuple(['1' if p >= 0 else '0' for p in projections[0]])  # Convert to tuple

        if hash_value not in hash_table:
            hash_table[hash_value] = []
        hash_table[hash_value].append(i)

# Function to find most similar texts based on LSH and threshold
def find_most_similar_texts(threshold):
    similar_texts = []

    for i in range(len(education_data)):
        for hash_table, random_vectors in zip(hash_tables, random_vectors_list):
            query_projections = np.dot(tf_idf[i].toarray(), random_vectors.T)
            query_hash_value = tuple(['1' if p >= 0 else '0' for p in query_projections[0]])

            if query_hash_value in hash_table:
                results = hash_table[query_hash_value]
                for doc_index in results:
                    if doc_index != i:
                        similarity = np.dot(tf_idf[i].toarray(), tf_idf[doc_index].toarray().T)
                        cosine_similarity = similarity[0, 0]  # Assuming both matrices are 1x1
                        if cosine_similarity >= threshold:
                            similar_texts.append((education_data[i], education_data[doc_index]))

    return similar_texts

# Examplea
threshold = 0.2
similar_texts = find_most_similar_texts(threshold)
# Convert pairs to frozensets and add to set to remove duplicates
unique_similar_texts = set(frozenset(pair) for pair in similar_texts)

# Convert frozensets back to pairs
unique_similar_texts = [tuple(pair) for pair in unique_similar_texts]

print(f"Unique pairs of similar education data above threshold {threshold}:")
for education_text_pair in unique_similar_texts:
    print(education_text_pair)

print(f"Number of unique pairs of similar education data above threshold {threshold}: {len(unique_similar_texts)}")


# Unique pairs of similar education data above threshold 0.6:
# ('Everest Polytechnic Master Fountainhead College PhD', 'Dunham University Bachelor Everest Polytechnic Master')
# ('Fountainhead College PhD Greenwood Academy Bachelor','Fountainhead College PhD Greenwood Academy Bachelor')
# ('Everest College PhD Greenwood Academy Bachelor', 'Fountainhead College PhD Greenwood Academy Bachelor')
# ('Yellowstone University Bachelor Yellowstone University Bachelor', 'Xenon Institute PhD Yellowstone University Bachelor')
# ('Pinnacle College Bachelor Quantum Academy Master', 'Quantum Academy Master Riverview Institute PhD')
# ('Ignite College Master Jubilee Institute PhD', 'Jubilee College Bachelor Jubilee College Bachelor')
# Number of unique pairs of similar education data above threshold 0.6: 6