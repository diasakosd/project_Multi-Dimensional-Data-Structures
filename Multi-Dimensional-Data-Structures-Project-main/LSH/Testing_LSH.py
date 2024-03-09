import csv
import sys
import time
import pprint

sys.path.append("./LSH")
import LSH

def main():

    # Read the scientist data from the csv file and store it in a list of points
    points = []
    with open(
        r".\Data\Tasting_LSH.csv", "r", encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)
        for row in reader:
            education = row["Education"]
            points.append((education))

    print(points)

    simil_thresh = 0.60
    start_time = time.time()
    similar_education_indexes = LSH.check_lsh_similarity(
        points, k=3, b=6, threshold=simil_thresh, hash_functions_count=12
    )
    lshend_time = time.time()
    lsh_time = lshend_time - start_time
    
    final_scientists = []
    for index in similar_education_indexes:
        row = points[index]
        final_scientists.append(row)

    print("\n".join(final_scientists))
        

   
    print(f'Lenght of Results: {len(similar_education_indexes)}')
    print(f"LSH similar indexes: {similar_education_indexes}")
    print(f"LSH time: {lsh_time}")
   
    

if __name__ == "__main__":
    main()  

