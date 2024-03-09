from random import shuffle
import csv
from itertools import combinations


class Shingling:
    """
    This class provides methods for generating shingles from text, creating a vocabulary from multiple sets of shingles,
    performing one-hot encoding, and creating zero vectors.
    """

    @staticmethod
    def shingle(text: str, k: int):
        """
        Generate shingles from the input text.

        Args:
        - text (str): The input text.
        - k (int): The length of each shingle.

        Returns:
        - set: A set of shingles.
        """
        shingles_set = []
        for i in range(len(text) - k + 1):
            shingles_set.append(text[i : i + k])
        return set(shingles_set)

    @staticmethod
    def create_vocabulary(shingle_sets: list):
        """
        Create a vocabulary by combining multiple sets of shingles.

        Args:
        - shingles_sets: Variable number of sets of shingles.

        Returns:
        - set: The combined vocabulary.
        """
        vocabulary = set()
        for shingle_set in shingle_sets:
            vocabulary = vocabulary.union(shingle_set)
        return vocabulary

    @staticmethod

    def create_zero_vector(size: int):
        """
        Create a zero vector of a given size.

        Args:
        - size (int): The size of the vector.

        Returns:
        - list: A zero vector.
        """
        return [0] * size

    @staticmethod
    def one_hot_encoding(shingle_set: str, vocabulary: set):
        """
        Perform one-hot encoding for the given text and vocabulary.

        Args:
        - text (str): The input text.
        - vocabulary (set): The vocabulary.

        Returns:
        - list: The sparse vector in one-hot encoding.
        """
        sparse_vector_one_hot = Shingling.create_zero_vector(len(vocabulary))
        for i, shingle in enumerate(vocabulary):
            if shingle in shingle_set:
                sparse_vector_one_hot[i] = 1
        return sparse_vector_one_hot


class MinHash:
    """
    This class implements the MinHash algorithm for generating minhash signatures.
    """

    def __init__(self, vocabulary_size: int, hash_functions_count: int):
        """
        Initialize the MinHash object with the given vocabulary size
        and the number of hash functions.

        Args:
        - vocabulary_size (int): The size of the vocabulary.
        - hash_functions_count (int): The number of hash functions to use.

        """

        self.vocabulary_size = vocabulary_size
        self.hash_functions_count = hash_functions_count
        self.min_hash_functions = self.build_min_hash_functions()

    def _create_hash_function(self):
        """
        Create a single hash vector/function as a shuffled vector of integers,
        of length vocabulary_size.

        Returns:
        - list: A shuffled vector representing the hash function.

        """

        min_hash_vector = list(range(1, self.vocabulary_size + 1))
        shuffle(min_hash_vector)
        return min_hash_vector

    def build_min_hash_functions(self):
        """
        Build a list of function for building multiple minhash vectors.

        Returns:
        - list: A list of hash functions.
        """
        minhash_functions = []
        for _ in range(self.hash_functions_count):
            minhash_functions.append(self._create_hash_function())

        return minhash_functions

    def minhash(self, sparse_vector: list):
        """
        Generate the minhash signature for the given sparse vector.

        Args:
        - sparse_vector (list): The one hot encoded sparse vector.

        Returns:
        - list: The minhash signature.
        """
        signature = []
        for hash_function in self.min_hash_functions:
            for i in range(1, self.vocabulary_size + 1):
                index = hash_function.index(i)
                if sparse_vector[index] == 1:
                    signature.append(i)
                    break
        return signature


class LSH:
    """
    This class implements the Locality Sensitive Hashing (LSH) algorithm for finding candidate pairs.
    """

    buckets = []
    index_counter = 0

    def __init__(self, b):
        """
        Initialize the LSH object with the number of bands.

        Args:
        - b (int): The number of bands.
        """
        self.b = b
        for i in range(b):
            self.buckets.append({})

    def split_signature_vector(self, signature):
        """
        Split the signature vector into b bands.

        Args:
        - signature (list): The signature vector.

        Returns:
        - list: The list of bands.
        """
        assert len(signature) % self.b == 0
        rows = int(len(signature) / self.b)
        subvecs = []
        for i in range(0, len(signature), rows):
            subvecs.append(signature[i : i + rows])

        return subvecs

    def add_signature_hash(self, signature):
        """Adds a signature hash to the appropriate buckets for efficient retrieval.

        Args:
            signature: The signature to be hashed and added.

        Returns:
            None
        """
        subvectors = self.split_signature_vector(signature)

        # Convert subvectors to strings for efficient handling within buckets
        subvector_strings = [[str(num) for num in subvec] for subvec in subvectors]

        # Iterate through each subvector string and its corresponding bucket
        for bucket_index, subvector_string in enumerate(subvector_strings):

            # Join subvector elements into a comma-separated string as the key
            subvector_string = ",".join(subvector_string)

            # Check if the subvector string exists as a key in the current bucket
            if subvector_string not in self.buckets[bucket_index]:
                # Create an empty list to hold signatures associated with this subvector
                self.buckets[bucket_index][subvector_string] = []

            # Append the current index counter to the list for this subvector string
            self.buckets[bucket_index][subvector_string].append(self.index_counter)

        # Increment the index counter for the next hash addition
        self.index_counter += 1

    def find_candidate_pairs(self):
        """
        Find candidate pairs based on the contents of the buckets.

        Returns:
        - set: A set containing all candidate pairs.
        """
        candidate_pairs = []

        # Explore each band of buckets
        for bucket_band in self.buckets:
            # Extract individual buckets
            keys = bucket_band.keys()

            # Iterate through each bucket (list of associated indices)
            for bucket in keys:
                hits = bucket_band[bucket]
                if len(hits) > 1:
                    candidate_pairs.extend(combinations(hits, 2))
        return set(candidate_pairs)


class Metrics:
    """
    This class provides methods for calculating Jaccard similarity and finding final education text indexes.
    """

    @staticmethod
    def jaccard_similarity(set_a: set, set_b: set):
        """
        Calculate the Jaccard similarity between two sets.

        Args:
        - set_a (set): The first set.
        - set_b (set): The second set.

        Returns:
        - float: The Jaccard similarity.
        """
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        jaccard_similarity = intersection / union
        return jaccard_similarity

    @staticmethod
    def find_final_education_indexes(
        candidate_pairs: set, signatures: list, threshold: float
    ) -> set:
        """
        Find final education text indexes based on candidate pairs and similarity threshold.

        Args:
        - candidate_pairs (set): Set of candidate pairs, where each pair is a tuple of indices.
        - signatures (list): List of MinHash signatures corresponding to texts.
        - threshold (float): Similarity threshold.

        Returns:
        - set: Set of final education text indexes.
        """
        final_education_text_indexes = set()

        # Iterate over candidate pairs and check similarity
        for pair in candidate_pairs:
            index_a, index_b = pair
            if (
                index_a not in final_education_text_indexes
                or index_b not in final_education_text_indexes
            ):
                signature_a = signatures[index_a]
                signature_b = signatures[index_b]
                similarity = Metrics.jaccard_similarity(
                    set(signature_a), set(signature_b)
                )
                if similarity >= threshold:
                    final_education_text_indexes.update([index_a, index_b])

        return final_education_text_indexes


def check_lsh_similarity(educations_list: list, k, b, threshold, hash_functions_count):
    """
    Check LSH similarity between education texts.

    Args:
    - educations_list (list): List of education texts.
    - k (int): The length of each shingle.
    - b (int): The number of bands.
    - threshold (float): Similarity threshold.
    - hash_functions_count (int): The number of hash functions to use.

    Returns:
    - set: Set of final education text indexes.
    """
    shingles = []
    for data in educations_list:
        shingle_set = Shingling.shingle(data, k)
        shingles.append(shingle_set)

    vocabulary = Shingling.create_vocabulary(shingles)

    shingles_onehot_encoding = []
    for shingle_set in shingles:
        onehot_encoding = Shingling.one_hot_encoding(shingle_set, vocabulary)
        shingles_onehot_encoding.append(onehot_encoding)

    minhash_instance = MinHash(
        vocabulary_size=len(vocabulary), hash_functions_count=hash_functions_count
    )
    signatures = []
    for sparse_vector in shingles_onehot_encoding:
        signature = minhash_instance.minhash(sparse_vector)
        signatures.append(signature)

    lsh_instance = LSH(b=b)
    for signature in signatures:
        lsh_instance.add_signature_hash(signature)

    candidate_pairs = lsh_instance.find_candidate_pairs()

    final_education_list_indexes = Metrics.find_final_education_indexes(
        candidate_pairs, signatures, threshold=threshold
    )

    return final_education_list_indexes


# For testing purposes
def main():
    """Reads education information from a CSV file and stores it in a Python array,
    then calls the find_candidate_pairs function to identify potential candidate pairs.
    """

    # Specify CSV file path
    csv_file_path = ".\Data\small_computer_scientists_data.csv"

    # Create an empty array to store education information
    education_data = []

    # Open the CSV file in read mode
    with open(csv_file_path, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            if row["Education"] != "":
                education_data.append(row["Education"])

    """--------------------Shingling--------------------"""

    k = 4  # shingle size
    # education_data = education_data[:50]
    # build shingles
    shingles = []
    for education_data in education_data:
        # Create shingle set
        shingle_set = Shingling.shingle(education_data, k)
        shingles.append(shingle_set)

    # Build vocabulary
    vocabulary = Shingling.create_vocabulary(shingles)

    # One-hot encode our shingles
    shingles_onehot_encoding = []
    for shingle_set in shingles:
        onehot_encoding = Shingling.one_hot_encoding(shingle_set, vocabulary)
        shingles_onehot_encoding.append(onehot_encoding)

    """--------------------MinHashing--------------------"""

    # Initialize MinHash instance and create the shuffled hash functions
    minhash_instance = MinHash(
        vocabulary_size=len(vocabulary), hash_functions_count=100
    )

    signatures = []
    for sparse_vector in shingles_onehot_encoding:
        signature = minhash_instance.minhash(sparse_vector)
        signatures.append(signature)

    """--------------------LSH function--------------------"""

    lsh_instance = LSH(b=25)  # Create an LSH instance with b bands

    for signature in signatures:
        lsh_instance.add_signature_hash(signature)

    candidate_pairs = lsh_instance.find_candidate_pairs()

    print(f"Candidate pairs: {candidate_pairs}")
    """print(f"Number of candidate pairs: {len(candidate_pairs)}")"""

    """--------------------Similarity Testing--------------------"""

    # Threshold for similarity
    threshold = 0.5

    final_education_indexes = Metrics.find_final_education_indexes(
        candidate_pairs, signatures, threshold=0.5
    )

    print(
        f"Final education text indexes with a similarity over {threshold*100}%: {final_education_indexes}"
    )


if __name__ == "__main__":

    main()
