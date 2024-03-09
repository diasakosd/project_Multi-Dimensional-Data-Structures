import math
import csv
import string
import time
import sys


class Scientist:
    """Represents a scientist with their surname, awards, education, and DBLP record.
    """
    def __init__(self, surname, awards, education, dblp_records):
        """Initializes a Scientist object.

        Args:
            surname: The scientist's surname (last name).
            awards: The number of awards the scientist has received.
            education: The scientist's educational background.
            dblp_records: The scientist's DBLP publication record.
        """

        self.surname = surname
        self.awards = awards
        self.education = education  # Add education attribute
        self.dblp_records = dblp_records


def read_csv(file_path):
    """Reads scientists' data from a CSV file.

    Args:
        file_path: The path to the CSV file.

    Returns:
        A list of Scientist objects representing the scientists in the CSV file.
    """
    scientists = []
    with open(file_path, "r", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)

        # Skip the header row if it exists
        header = next(csv_reader, None)

        for row in csv_reader:
            # Print each row to debug
            # print("Processing row:", row)

            if len(row) == 4:  # Assuming 4 columns in the CSV
                surname, awards, education, dblp_records = map(str.strip, row)

                # Try converting awards, dblp_records to float
                try:
                    awards = float(awards)
                    dblp_records = float(dblp_records)
                    scientist = Scientist(surname, awards, education, dblp_records)
                    scientists.append(scientist)
                except ValueError:
                    # Handle the case where conversion to float fails
                    # print(f"Skipping row due to invalid numeric value: {row}")
                    pass  # Consider skipping the row silently in case of conversion failure

    return scientists


class MinimumBoundingObject:
    """Represents a minimum bounding object in a multi-dimensional space."""
    def __init__(self, low, high):
        """Initializes a MinimumBoundingObject.

        Args:

            low: A list representing the lower bounds in each dimension.

            high: A list representing the upper bounds in each dimension.
        """
        self.low = low
        self.high = high
        self.child = None

    def __str__(self, level=0):
        """

        Args:

            level: The indentation level for formatting.

        Returns:
            A string representation of the MinimumBoundingObject and its children.
        """
        prefix = "| " * level
        result = f"{prefix}Bounding Object: {self.low} to {self.high}\n"
        if self.child:
            result += self.child.__str__(level + 1)
        return result


def convert_to_mapping(value):
    """Converts a value to a mapping for comparison in the R-tree.

    Handles both string and numeric values. Strings are converted to uppercase
    and then to an ordinal value (starting from A -> 1).

    Args:
        value: The value to convert.

    Returns:
        The mapped value.
    """
    if isinstance(value, str):
        return ord(value[0].upper()) - 64 # 64 to shift 'A' to 1
    else:
        return float(value)


def minimum_bounding_object_calculator(points, dimensions):
    """Calculates the minimum bounding object for a list of points.
       
    Args:
    
            points: A list of points to calculate the minimum bounding object for.
    
            dimensions: The number of dimensions in the space.

    Returns:
        A MinimumBoundingObject representing the minimum bounding object for the points.
    """
    if not points:
        # Handle the case where the points list is empty
        return None

    if isinstance(points[0], MinimumBoundingObject):
        starting_index = 0
        ending_index = dimensions
        lower = [float("inf")] * dimensions
        upper = [float("-inf")] * dimensions
    else:
        starting_index = 0  # Change to 0 instead of 1
        ending_index = dimensions
        lower = [float("inf")] * dimensions
        upper = [float("-inf")] * dimensions

    for point in points:
        for i in range(starting_index, ending_index):
            try:
                if isinstance(point, MinimumBoundingObject):
                    if convert_to_mapping(point.low[i]) < lower[i]:
                        lower[i] = convert_to_mapping(point.low[i])
                    elif convert_to_mapping(point.high[i]) > upper[i]:
                        upper[i] = convert_to_mapping(point.high[i])
                else:
                    # Handle the case where the element is a Scientist object
                    value = convert_to_mapping(
                        getattr(point, ["surname", "awards", "dblp_records"][i])
                    )
                    if value < lower[i]:
                        lower[i] = value
                    elif value > upper[i]:
                        upper[i] = value
            except IndexError as e:
                # print(f"Error processing point: {point}")
                # print(e)
                raise

    return MinimumBoundingObject(lower, upper)


class Node:
    """ Represents   node in the R-tree data structure."""
    def __init__(self, items):
        """Initializes a Node object.

        Args:
            items: A list of items stored in the node. Items can be either 
                   MinimumBoundingObject instances or Scientist objects.
        """

        self.items = items

    def __str__(self, level=0):
        """Creates a string representation of the Node and its children.

        Args:
            level: The indentation level for formatting.

        Returns:
            A string representation of the Node and its children.
        """

        prefix = "| " * level
        result = f"{prefix}Node:\n"
        for item in self.items:
            if isinstance(item, MinimumBoundingObject):
                result += f"{prefix}  - Bounding Object: {item.low} to {item.high}\n"
                result += item.child.__str__(level + 1)
            else:
                result += f"{prefix}  - Item: {item.surname, item.awards, item.dblp_records}\n"
        return result


class RTree:
    """Represents an R-tree data structure for spatial indexing."""
    def __init__(self):
        """Initializes an empty RTree."""
        self.root = None  # Initialize the root attribute

    def create_rtree(self, points, dimensions):
        """Builds an R-tree from a list of points (each point is a 
           Scientist object).

        Args:
            points: A list of points where each point can be either a 
                    Scientist or a MinimumBoundingObject.
            dimensions: The number of dimensions (attributes).

        Returns:
            The root node of the constructed R-tree.
        """
        M = 4
        m = 2
        upper_level_items = []

        if not points:
            # print("No points provided.")
            return None

        if 0 < len(points) % M < m:
            remaining_points = M + len(points) % M
            last_two_groups_length = [
                math.ceil(remaining_points / m),
                math.floor(remaining_points / m),
            ]
        elif len(points) % M >= m:
            last_two_groups_length = [M, len(points) % M]
        else:
            if len(points) == M:
                last_two_groups_length = [M, 0]
            else:
                last_two_groups_length = [M, M]

        # uncomment for tasting the last two groups length
        # print("Points:", points)
        # print("Last two groups length:", last_two_groups_length)

        for i in range(math.ceil((len(points) / M)) - 2):
            items_per_group = M
            new_minimum_bounding_object = minimum_bounding_object_calculator(
                points[:items_per_group], dimensions
            )
            if new_minimum_bounding_object:
                new_minimum_bounding_object.child = Node(points[:M])  # Set the child attribute
                upper_level_items.append(new_minimum_bounding_object)
                del points[:M]

        for i in range(len(last_two_groups_length)):
            items_per_group = last_two_groups_length[i]
            new_minimum_bounding_object = minimum_bounding_object_calculator(
                points[:items_per_group], dimensions
            )
            if new_minimum_bounding_object:
                new_minimum_bounding_object.child = Node(points[:items_per_group])
                upper_level_items.append(new_minimum_bounding_object)
                del points[:items_per_group]

        # print("Upper-level items:", upper_level_items)

        if not upper_level_items:
            # print("No upper-level items created.")
            return None

        if len(upper_level_items) <= M:
            self.root = Node(upper_level_items)  # Set the root attribute
            return self.root
        else:
            return self.create_rtree(upper_level_items, dimensions)
        
    def convert_to_mapping(self, value):
        """Converts strings to ordinal representation, floats are directly used.

        Args:
            value: The value to be converted.

        Returns:
            The mapped value.
        """
        if isinstance(value, str):
            return ord(value[0].upper()) - 64
        else:
            return float(value)

    def query(self, root, surname_range, min_awards, dblp_range):
        """Performs a range search query on the R-tree.

        Args:
            root: The root node of the R-tree.

            surname_range: A tuple representing the range of surnames to search.

            min_awards: The minimum number of awards.

            dblp_range: A tuple representing the range of DBLP records to search.
        
        Returns:
            A list of surnames that match the search criteria.
        """
        results = []
        current_node = root

        if current_node is None:
            print("Current node is None")
            return None  # Return None if the current node is None

        if current_node.items:
            if isinstance(current_node.items[0], MinimumBoundingObject):
                for item in current_node.items:
                    result = self.query(
                        item.child, surname_range, min_awards, dblp_range
                    )
                    if result is not None:
                        results += result
            else:
                for scientist in current_node.items:
                    # Check if the current scientist is within the specified range for the surname
                    surname_value = self.convert_to_mapping(scientist.surname)
                    if (
                        self.convert_to_mapping(surname_range[0])
                        <= surname_value
                        <= self.convert_to_mapping(surname_range[1])
                    ):
                        # Check if awards, dblp_records, and dblp_range meet the criteria
                        if (
                            scientist.awards > min_awards
                            and dblp_range[0] <= scientist.dblp_records <= dblp_range[1]
                        ):
                            results.append(scientist.surname)  # Append the surname

        return results

    def __str__(self):
        """Creates a string representation of the R-tree.

        Returns:

            A string representation of the R-tree.
        """

        if self.root is None:
            return "Empty RTree"
        return self.create_rtree_str(self.root)

    def create_rtree_str(self, node, level=0):
        """Creates a string representation of the R-tree.

        Args:

            node: The current node in the R-tree.

            level: The indentation level for formatting.

        Returns:

            A string representation of the R-tree.
        """

        if node is None:
            return ""

        prefix = "| " * level
        result = ""

        if hasattr(node, "child") and node.child is not None:
            if isinstance(node.items[0], MinimumBoundingObject):
                result += f"{prefix}Bounding Object: {node.items[0].low} to {node.items[-1].high}\n"
            else:
                result += f"{prefix}Bounding Object: {node.items[0][0]} to {node.items[-1][0]}\n"

            if isinstance(node.child, Node):
                result += self.create_rtree_str(node.child, level + 1)
            elif isinstance(node.child, list):
                for child in node.child:
                    result += self.create_rtree_str(child, level + 1)
        else:
            # Leaf node, display individual items
            for item in node.items:
                result += f"{prefix}Leaf: {item}\n"

        return result


def load_scientists_from_csv(csv_file, scientists):
    """Loads scientists' data from a CSV file.

    Args:


        csv_file: The path to the CSV file.

        scientists: A list to store the Scientist objects.
    """

    with open(csv_file, mode="r", encoding="utf-8") as csvfile:
        csv_reader = csv.reader(csvfile)
        header = next(csv_reader, None)

        for row in csv_reader:
            # Check if the row has enough columns
            if len(row) != 4:
                continue  # Skip rows with an incorrect number of columns

            surname, awards, education, dblp_record = map(str.strip, row)

            # Skip rows with non-numeric 'Awards' and 'DBLP Info' values
            if not awards.isdigit() or not dblp_record.isdigit():
                continue

            scientists.append(
                Scientist(surname, int(awards), education, int(dblp_record))
            )




def main():
    # Check if the correct number of command-line arguments are provided
    if len(sys.argv) != 4:
        print(
            "Usage: python script_name.py <surname_range> <awards_threshold> <dblp_range>\nExample: python rtree.py A-T 1 20-1000\n"
        )
        return
    # Example usage:
    start_time_total=time.time()
    scientists_list = []
    csv_file_path = r".\Data\new_computer_scientists_data.csv"
    load_scientists_from_csv(csv_file_path, scientists_list)
    dimensions = 3

    start_time = time.time()
    rtree = RTree()
    # Read data from CSV and create the R-tree
    scientists_from_csv = read_csv(csv_file_path)
    rtree.create_rtree(scientists_from_csv, dimensions)
    end_time = time.time()
    build_time = end_time - start_time


    # Parse command-line arguments
    surname_range = tuple(sys.argv[1].split("-"))
    awards_threshold = int(sys.argv[2])
    dblp_range = tuple(map(int, sys.argv[3].split("-")))

    # Example range search query with surname range (A to D), min awards (4), and min dlp_records (20,300):
    start_time = time.time()
    range_query_result = rtree.query(rtree.root,surname_range, awards_threshold,dblp_range)
    end_time = time.time()
    search_time = end_time - start_time
    search_results = []
    

    # Print education of the first scientist in the result
    if range_query_result:
        for scientist in scientists_list:
            if scientist.surname in range_query_result:
                print("--------------------------------------")
                print(
                    f"{scientist.surname}, awards: {scientist.awards}, dblp_records: {scientist.dblp_records}"
                )
                print(f"Education: {scientist.education}")
                print("--------------------------------------")
                search_results.append(scientist)

    """-------LSH Similarity Queries------------"""
    sys.path.append("LSH")
    import LSH
    # Create the educations list
    educations = []

    for result in search_results:
        educations.append(result.education)  # Education string is at position 3
        
    simil_thresh = 0.5
    start_time = time.time()
    similar_education_indexes = LSH.check_lsh_similarity(
        educations, k=4, b=25, threshold=simil_thresh, hash_functions_count=100
    )
    lshend_time = time.time()
    lsh_time = lshend_time - start_time
    total_time=lshend_time-start_time_total
    # Print the final scientist data with similar educations
    print(
        f"\nScientists with Similarity above {simil_thresh*100}% ({len(similar_education_indexes)}):"
    )

    final_scientists = []
    for index in similar_education_indexes:
        row = search_results[index].surname
        final_scientists.append(row)
        # Print the scientist data
        print(
            f"\nName: {search_results[index].surname}, \nAwards: {search_results[index].awards}, \nEducation: {search_results[index].education}, \nDBLP Record: {search_results[index].dblp_records}"
        )
        
    print(f"\nNumber of scientists in the result: {len(range_query_result)}")        
    # Print execution time results
    print("\nExecution Time Results:")
    print(f"\nBuild Time: {build_time} seconds")
    print(f"Search Time: {search_time} seconds")
    print(f"LSH Time: {lsh_time} seconds")
    print(f"Total Time: {total_time} seconds")      

if __name__ == "__main__":
    main()
