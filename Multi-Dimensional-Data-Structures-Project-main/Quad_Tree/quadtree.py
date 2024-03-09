import csv
import sys
import time

class Scientist:
    """Represents a scientist with their surname, awards, education, and DBLP record.
    """
    def __init__(self, surname, awards, education, dblp_record):
        """Initializes a Scientist object.

            Args:
                surname: The scientist's surname (last name).
                awards: The number of awards the scientist has received.
                education: The scientist's educational background.
                dblp_record: The scientist's DBLP publication record.
        """
        self.surname = surname
        self.awards = awards
        self.education = education
        self.dblp_record = dblp_record

class Node():
    """Node in a quadtree data structure.

    A quadtree recursively subdivides a space into smaller regions for
    efficient spatial queries.
    """
    def __init__(self, x0, y0, z0, w, h, d, scientists):
        """Initializes Node object.

        Args:

            x0: The x-coordinate of the node's lower-left corner.
            y0: The y-coordinate of the node's lower-left corner.
            z0: The z-coordinate of the node's lower-left corner.

            w: The width of the node.
            h: The height of the node.
            d: The depth of the node.
            
            scientists: A list of Scientist objects contained within the node.

        """
        self.x0 = x0
        self.y0 = y0
        self.z0 = z0
        self.width = w
        self.height = h
        self.depth = d
        self.scientists = scientists
        self.children = []

    def get_width(self):
        """Returns the width of the node."""
        return self.width

    def get_height(self):
        """Returns the height of the node."""
        return self.height

    def get_depth(self):
        """Returns the depth of the node."""
        return self.depth

    def get_scientists(self):
        """Returns the list of scientists contained within the node."""
        return self.scientists

def recursive_subdivide(node, surname_range, awards_threshold, dblp_range):
    """Recursively subdivides a quadtree node into smaller segments.

    This function subdivides a node until it contains a small enough
    number of scientists or cannot be subdivided further. Filtering based
    on surname, awards and DBLP record is included.

    Args:
        node: The Node object to subdivide.
        surname_range: A tuple containing the starting and ending letters 
            of the surname range for filtering.
        awards_threshold: The minimum number of awards for a scientist
            to be included.
        dblp_range: A tuple containing the minimum and maximum DBLP
            records for a scientist to be included.

    Returns:
         A list of Node objects representing the leaf node segments.
    """
   
    if len(node.scientists) <= 2:
        return [node]  # Return the current node as a segment

    # Filtering scientists based on user-defined criteria
    filtered_scientists = [s for s in node.scientists if
                           ord(surname_range[0]) <= ord(s.surname[0]) <= ord(surname_range[1]) and
                           s.awards > awards_threshold and
                           dblp_range[0] <= s.dblp_record <= dblp_range[1]]

    if len(filtered_scientists) == 0:
        return [node] # Return the current node as a segment
    # Divide Node into 8 smaller nodes
    w_ = float(node.width / 2)
    h_ = float(node.height / 2)
    d_ = float(node.depth / 2)

    p = contains(node.x0, node.y0, node.z0, w_, h_, d_, filtered_scientists)
    x1 = Node(node.x0, node.y0, node.z0, w_, h_, d_, p)
    children1 = recursive_subdivide(x1, surname_range, awards_threshold, dblp_range)

    p = contains(node.x0, node.y0 + h_, node.z0, w_, h_, d_, filtered_scientists)
    x2 = Node(node.x0, node.y0 + h_, node.z0, w_, h_, d_, p)
    children2 = recursive_subdivide(x2, surname_range, awards_threshold, dblp_range)

    p = contains(node.x0 + w_, node.y0, node.z0, w_, h_, d_, filtered_scientists)
    x3 = Node(node.x0 + w_, node.y0, node.z0, w_, h_, d_, p)
    children3 = recursive_subdivide(x3, surname_range, awards_threshold, dblp_range)

    p = contains(node.x0 + w_, node.y0 + h_, node.z0, w_, h_, d_, filtered_scientists)
    x4 = Node(node.x0 + w_, node.y0 + h_, node.z0, w_, h_, d_, p)
    children4 = recursive_subdivide(x4, surname_range, awards_threshold, dblp_range)

    p = contains(node.x0, node.y0, node.z0 + d_, w_, h_, d_, filtered_scientists)
    x5 = Node(node.x0, node.y0, node.z0 + d_, w_, h_, d_, p)
    children5 = recursive_subdivide(x5, surname_range, awards_threshold, dblp_range)

    p = contains(node.x0, node.y0 + h_, node.z0 + d_, w_, h_, d_, filtered_scientists)
    x6 = Node(node.x0, node.y0 + h_, node.z0 + d_, w_, h_, d_, p)
    children6 = recursive_subdivide(x6, surname_range, awards_threshold, dblp_range)

    p = contains(node.x0 + w_, node.y0, node.z0 + d_, w_, h_, d_, filtered_scientists)
    x7 = Node(node.x0 + w_, node.y0, node.z0 + d_, w_, h_, d_, p)
    children7 = recursive_subdivide(x7, surname_range, awards_threshold, dblp_range)

    p = contains(node.x0 + w_, node.y0 + h_, node.z0 + d_, w_, h_, d_, filtered_scientists)
    x8 = Node(node.x0 + w_, node.y0 + h_, node.z0 + d_, w_, h_, d_, p)
    children8 = recursive_subdivide(x8, surname_range, awards_threshold, dblp_range)

    node.children = [x1, x2, x3, x4, x5, x6, x7, x8]
    return [node] + children1 + children2 + children3 + children4 + children5 + children6 + children7 + children8



def contains(x, y, z, w, h, d, scientists):
    """Checks if any scientists fall within a given region of the space.

    Args:
        x: The x-coordinate of the region's lower-left corner.
        y: The y-coordinate of the region's lower-left corner.
        z: The z-coordinate of the region's lower-left corner.
        w: The width of the region.
        h: The height of the region.
        d: The depth of the region.
        scientists: A list of Scientist objects.

    Returns:
        A list of Scientist objects that fall within the specified region.
    """
    scientists_inside = []
    for scientist in scientists:
        first_char = ord(scientist.surname[0]) if scientist.surname else 0
        if x <= first_char <= x + w and \
           y <= scientist.awards <= y + h and \
           z <= scientist.dblp_record <= z + d:
            scientists_inside.append(scientist)
    return scientists_inside


class QTree():
    """A quadtree data structure for efficient multi-dimensional spatial queries.
    """
    def __init__(self, surname_range, awards_threshold, dblp_range, scientists=None):
        """Initializes a QuadTree object.

        Args:
            surname_range: A tuple typw of containing the starting and ending letters 
                 of the surname range.
            awards_threshold: The minimum number of awards for scientists.
            dblp_range: A tuple containing the minimum and maximum DBLP
                records for scientists.
            scientists: An optional initial list of Scientist objects.
        """

        self.surname_range = surname_range
        self.awards_threshold = awards_threshold
        self.dblp_range = dblp_range

        if scientists is None:
            scientists = []

        self.scientists = scientists
        self.root = Node(0, 0, 0, 1000, 1000, 1000, self.scientists)

    def add_scientist(self, surname, awards, education, dblp_record):
        """Adds a new scientist to the quadtree.

        Args:
            surname: The scientist's surname.
            awards: The number of awards the scientist has received.
            education: The scientist's educational background.
            dblp_record: The scientist's DBLP publication record.
        """

        self.scientists.append(Scientist(surname, awards, education, dblp_record))

    def load_scientists_from_csv(self, csv_file):
        """Loads scientists from a CSV file into the quadtree.

        Args:
            csv_file: The path to the CSV file.
        """

        with open(csv_file, mode='r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            header = next(csv_reader, None)

            if header is not None:
                # Handle headers here if needed
                # You can print, process, or skip them based on your requirements
                print("CSV Headers:", header)

            for row in csv_reader:
                # Check if the row has enough columns
                if len(row) != 4:
                    continue  # Skip rows with an incorrect number of columns

                surname, awards, education, dblp_record = map(str.strip, row)

                # Skip rows with non-numeric 'Awards' and 'DBLP Info' values
                if not awards.isdigit() or not dblp_record.isdigit():
                    continue

                self.add_scientist(surname, int(awards), education, int(dblp_record))

    def subdivide(self):
        """Subdivides the quadtree recursively based on filtering criteria."""
        recursive_subdivide(self.root, self.surname_range, self.awards_threshold, self.dblp_range)

def query_quadtree(quadtree, surname_range, awards_threshold, dblp_range):
    """Queries the quadtree to find scientists matching the specified criteria.

    Args:
        quadtree: The QTree object to query.
        surname_range: A tuple containing the starting and ending letters 
            of the surname range for filtering.
        awards_threshold: The minimum number of awards for a scientist
            to be included.
        dblp_range: A tuple containing the minimum and maximum DBLP
            records for a scientist to be included.

    Returns:
        A list of Scientist objects that match the query criteria.
    """
    result = set()  # Use a set to avoid duplicates

    def traverse_and_query(node):
        if not node:
            return

        for scientist in node.get_scientists():
            surname = scientist.surname
            awards = scientist.awards
            dblp = scientist.dblp_record

            if (ord(surname_range[0]) <= ord(surname[0]) <= ord(surname_range[1])) and \
            (awards > awards_threshold) and \
            (dblp_range[0] <= dblp <= dblp_range[1]):
                result.add(scientist)

        for child in node.children:
            traverse_and_query(child)

    traverse_and_query(quadtree.root)
    return list(result)


def main():
    
    # Check if the correct number of command-line arguments are provided
    if len(sys.argv) != 4:
        print(
            "Usage: python script_name.py <surname_range> <awards_threshold> <dblp_range>\nExample: python quadtree.py A-T 1 20-1000\n"
        )
        return
    start_time_total=time.time()
    start_time=time.time()
    # Creating an instance of the QTree class with manually added and randomly generated scientists
    quadtree = QTree(surname_range=('A', 'Z'), awards_threshold=-1, dblp_range=(1, 100000))

    # Loading scientists from CSV file
    quadtree.load_scientists_from_csv(r".\Data\new_computer_scientists_data.csv")
    end_time=time.time()
    build_time=end_time-start_time

    # Parse command-line arguments
    surname_range = tuple(sys.argv[1].split("-"))
    awards_threshold = int(sys.argv[2])
    dblp_range = tuple(map(int, sys.argv[3].split("-")))

    start_time=time.time()
    # Query scientists based on user-defined criteria
    results = query_quadtree(quadtree, surname_range, awards_threshold, dblp_range)
    end_time=time.time()
    search_time=end_time-start_time

    

    # Print education of the first scientist in the result
    if results:
        for scientist in results:
            print("--------------------------------------")
            print(f"{scientist.surname}, awards: {scientist.awards}, dblp_records: {scientist.dblp_record}")
            print(f"Education: {scientist.education}")
            print("--------------------------------------")
            
    
    """-------LSH Similarity Queries------------"""
    sys.path.append("LSH")
    import LSH
    # Create the educations list
    educations = []

    for result in results:
        educations.append(result.education)  # Education string is at position 3
    
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
        row = results[index].surname
        final_scientists.append(row)
        # Print the scientist data
        print(
            f"\nName: {results[index].surname}, \nAwards: {results[index].awards}, \nEducation: {results[index].education}, \nDBLP Record: {results[index].dblp_record}"
        )

    print(f"\nScientists found: {len(results)}")
    # Print execution time results
    print("\nExecution Time Results:")
    print(f"\nBuild Time: {build_time} seconds")
    print(f"Search Time: {search_time} seconds")
    print(f"LSH Time: {lsh_time} seconds")
    print(f"Total Time: {total_time} seconds")
  
if __name__ == "__main__":
    main()




