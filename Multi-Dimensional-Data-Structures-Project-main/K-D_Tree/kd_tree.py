import pandas as pd
import csv
import pprint
import time
import sys

sys.path.append("./LSH")
import LSH

k = 3


def build_kdtree(points, depth=0):
    """
    Build a k-d tree from the given points.

    Parameters:
    - points: a list of points to build the k-d tree from
    - depth: the current depth of the k-d tree (default is 0)

    Returns:
    - A dictionary representing the k-d tree
    """
    n = len(points)

    if n <= 0:
        return None

    axis = depth % k

    sorted_points = sorted(points, key=lambda point: point[axis])

    return {
        "point": sorted_points[n // 2],
        "left": build_kdtree(sorted_points[: n // 2], depth + 1),
        "right": build_kdtree(sorted_points[n // 2 + 1 :], depth + 1),
    }


def search_tree(tree, surname_range, awards_threshold, dblp_range, depth=0):
    """
    Search the given tree for points that satisfy the given criteria within the specified ranges.

    Args:
        tree: The tree to search.
        surname_range: The range of surname values to search within.
        awards_threshold: The minimum awards threshold to search for.
        dblp_range: The range of dblp values to search within.
        depth: The depth of the current node in the tree. Defaults to 0.

    Returns:
        A list of points that satisfy the given criteria within the specified ranges.
    """
    result = []

    if tree is None:
        return []

    axis = depth % k
    point = tree["point"]

    if (
        surname_range[0] <= point[0][0] <= surname_range[1]
        and point[1] > awards_threshold
        and dblp_range[0] <= point[2] <= dblp_range[1]
    ):
        result = [point]

    # name ε [surname_range[0], surname_range[1]
    if axis == 0:
        if surname_range[0] <= point[axis][0]:
            result += search_tree(
                tree["left"], surname_range, awards_threshold, dblp_range, depth + 1
            )

        if surname_range[1] >= point[axis][0]:
            result += search_tree(
                tree["right"], surname_range, awards_threshold, dblp_range, depth + 1
            )

    # awards > awards_threshold
    elif axis == 1:
        if awards_threshold <= point[axis]:
            result += search_tree(
                tree["left"], surname_range, awards_threshold, dblp_range, depth + 1
            )
            result += search_tree(
                tree["right"], surname_range, awards_threshold, dblp_range, depth + 1
            )

        elif awards_threshold >= point[axis]:
            result += search_tree(
                tree["right"], surname_range, awards_threshold, dblp_range, depth + 1
            )
    # dblp ε [dblp_range[0], dblp_range[1]]
    elif axis == 2:
        if dblp_range[0] <= point[axis]:
            result += search_tree(
                tree["left"], surname_range, awards_threshold, dblp_range, depth + 1
            )

        if dblp_range[1] >= point[axis]:
            result += search_tree(
                tree["right"], surname_range, awards_threshold, dblp_range, depth + 1
            )

    return result


def main():
    # Check if the correct number of command-line arguments are provided
    if len(sys.argv) != 4:
        print(
            "Usage: python script_name.py <surname_range> <awards_threshold> <dblp_range>\nExample: python kd_tree.py A-T 1 20-1000\n"
        )
        return
    start_time_total=time.time()
    # Read the scientist data from the csv file and store it in a list of points
    points = []
    with open(
        r".\Data\small_computer_scientists_data.csv", "r", encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)
        for row in reader:
            surname = row["Surname"]
            awards = int(row["Awards"])
            education = row["Education"]
            dblp_record = int(row["DBLP Info"])
            points.append((surname, awards, dblp_record, education))

    # Displaying the list of points
    pp = pprint.PrettyPrinter(indent=4)

    # For Testing only
    """print("Points:")
    pp.pprint(points)"""

    """-------K-D Tree Construction------------"""
    start_time = time.time()
    kd_tree = build_kdtree(points)
    end_time = time.time()
    build_time = end_time - start_time

    # For Testing only
    #print(f"\n3D Tree ({len(points)} entries):\n")
    #pp.pprint(kd_tree)

    """-------K-D Tree Search------------"""
    # Parse command-line arguments
    surname_range = tuple(sys.argv[1].split("-"))
    awards_threshold = int(sys.argv[2])
    dblp_range = tuple(map(int, sys.argv[3].split("-")))

    start_time = time.time()
    search_results = search_tree(kd_tree, surname_range, awards_threshold, dblp_range)
    end_time = time.time()
    search_time = end_time - start_time

    # For Testing only
    #print(f"\nSearch Results ({len(search_results)}):")
    # pp.pprint(search_results)

    """-------LSH Similarity Queries------------"""

    # Create the educations list
    educations = []

    for result in search_results:
        educations.append(result[3])  # Education string is at position 3

    simil_thresh = 0.5
    start_time = time.time()
    similar_education_indexes = LSH.check_lsh_similarity(
        educations, k=4, b=25, threshold=simil_thresh, hash_functions_count=100
    )
    lshend_time = time.time()
    lsh_time = lshend_time - start_time
    total_time = lshend_time - start_time_total
 
    # Print the final scientist data with similar educations
    print(
        f"\nScientists with Similarity above {simil_thresh*100}% ({len(similar_education_indexes)}):"
    )

    final_scientists = []
    for index in similar_education_indexes:
        row = search_results[index]
        final_scientists.append(row)
        # Print the scientist data
        print(
            f"\nName: {row[0]}, \nAwards: {row[1]}, \nEducation: {row[3]}, \nDBLP Record: {row[2]}"
        )
    
    print(f"\nSearch Results ({len(search_results)}):")
    # Print execution time results
    print("\nExecution Time Results:")
    print(f"\nBuild Time: {build_time} seconds")
    print(f"Search Time: {search_time} seconds")
    print(f"LSH Time: {lsh_time} seconds")
    print(f"Total Time: {total_time} seconds")

if __name__ == "__main__":
    main()
