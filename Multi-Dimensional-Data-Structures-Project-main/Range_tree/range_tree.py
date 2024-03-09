import csv
import sys
import time
import pprint

sys.path.append("./LSH")
import LSH

class Node:
    """
    A class representing a node in a range tree.
    Each node contains a value, a left child, and a right child, as well as a 1D range tree for the z-coordinates of the points.
    """
    def __init__(self, left=None, right=None, value=None, y_tree=None , z_tree=None , education=None ):
        """
        Initializes a new node with the given left and right children, value, and 1D range tree.

        Parameters:
        - left: The left child of the node.
        - right: The right child of the node.
        - value: The value of the node.
        - y_tree: The 1D range tree for the y-coordinates of the points.
        - z_tree: The 2D range tree for the z-coordinates of the points.
        - education: The education of the node.
        """
        self.left = left
        self.right = right
        self.value = value
        self.y_tree = y_tree
        self.z_tree = z_tree    
        self.education = education

class RangeTree1D:
    """
        RangeTree1D is a class that represents a 1-dimensional range tree.
        It's a data structure that allows you to efficiently query ranges of points along a single axis. 
        The class is implemented as a binary search tree where the nodes represent points and each node has
        a left and a right child representing the points that are less than or greater than the point at the node, respectively. 
    """
    def __init__(self, points, axis=0):
        """
         The init method is the constructor for the class and takes two inputs:
                points: A list of points in 1D space represented z coordinate
                axis: decides on which dimension to sort each time in this tree it will be always 2 for 1d  tree of the 3d RangeTree
        """
        self.axis = axis
        self.root = self._build_tree(points)

    def _build_tree(self, points):
        """
        The _build_tree method is a recursive method that takes two inputs:
                points: A list of points in 1D space represented z coordinate
        It builds the 1D range tree recursively by dividing the input points into left and right subsets,
        according to the median of the z-coordinates of the points.
        This method is called during initialization and should not be called directly.

        """
        if not points: return None

        if len(points) == 1:
            return Node(value=points[0])

        points.sort(key=lambda point: point[self.axis])

        median = len(points) // 2

        left = RangeTree1D(points[:median], axis=self.axis)
        right = RangeTree1D(points[median+1:], axis=self.axis)
        
        return Node(left=left, right=right, value=points[median])


    def query(self, z_range):
            """
            The query method is a recursive method that takes two inputs:
                    z_range: A tuple representing the z-range of the query, in the form (z_min, z_max).
            It performs a range search on the 1D range tree, returning all points that fall within the given z-range.
            The search starts at the root of the tree and recursively traverses the left and right subtrees,
            depending on the location of the query range relative to the current node.

            """

            if not self.root: return []

            values = []
            if z_range[0] <= self.root.value[self.axis] <= z_range[1]:
                values.append(self.root.value)

            if self.root.left:
                values += self.root.left.query(z_range)
            if self.root.right:
                values += self.root.right.query(z_range)
            
            return values


class RangeTree2D:
    """
        A 2D range tree implementation that allows for efficient range searches in two dimensions.
        The tree is constructed using a balanced binary search tree, where each node represents a split in the data along one of the dimensions.
        Additionally, each node also contains a 1D range tree of the data points that fall within its region, to allow for 
        efficient searches along the other dimension.
    """

    def __init__(self, points, axis=0):
        """
            Initializes a 2D range tree with the given list of points. The tree is balanced based on the y-coordinates of
            the points by default, but the axis can be changed by setting the axis parameter to 1.
            
            Parameters:
            - points (List[Tuple[int, int]]): A list of (y, z) tuples representing the points in the tree.
            - axis (int): The axis to use for the initial split (default: 0, which corresponds to the x-axis)
        """

        self.axis = axis
        self.root = self._build_tree(points)


    def _build_tree(self, points):
        """
            Builds the 2D range tree recursively by dividing the input points into left and right subsets,
            according to the median of the y-coordinates of the points.

            This method is called during initialization and should not be called directly.


            Parameters:
            - points (List[Tuple[int, int]]): A list of (y, z) tuples representing the points in the tree.

            Returns:
            - Node: The root node of the tree.
        """

        if not points:
            return None

        if len(points) == 1:
            return Node(value=points[0], z_tree=RangeTree1D(points, axis=2))

        # sort by x coord
        points.sort(key=lambda point: point[self.axis])
    
        median = len(points) // 2

        left_points = points[:median]
        right_points = points[median+1:]
        # In RangeTree2D
        left = RangeTree2D(left_points, axis=self.axis) if left_points else None
        right = RangeTree2D(right_points, axis=self.axis) if right_points else None

        return Node(left=left, right=right, value=points[median], z_tree=RangeTree1D(points, axis=2))

    def range_search(self, y_range, z_range):
        """
            Performs a range search on the 2D range tree, returning all points that fall within the given y-range.
            The search starts at the root of the tree and recursively traverses the left and right subtrees,
            depending on the location of the query range relative to the current node. 
        
            Parameters:
            - y_range (Tuple[int, int]): A tuple representing the y-range of the query, in the form (y_min, y_max).
            - z_range (Tuple[int, int]): A tuple representing the z-range of the query, in the form (z_min, z_max).

            Returns:
            - List[Tuple[int, int]]: A list of (y, z) tuples representing the points in the tree that fall within
            the given y-range and z-range.

        """
        if self.root is None: return []
 
        if y_range[0] <= self.root.value[self.axis] <= y_range[1]:
            # Return only the points in the y_tree that fall within the x-range of the query
            return [point for point in self.root.z_tree.query(z_range) if y_range[0] < point[1] < y_range[1]]
            # return self.root.y_tree.query(y_range)
        
        values = []

        # Traverse the left and right subtrees based on the location of the query range relative to the current node


        if y_range[0] >= self.root.value[self.axis]:
            if self.root.right:
                values += self.root.right.range_search(y_range, z_range)
        elif y_range[1] <= self.root.value[self.axis]:
        
            if self.root.left:
                values += self.root.left.range_search(y_range, z_range)
        return values
class RangeTree3D:

    """
        A 3D range tree implementation that allows for efficient range searches in three dimensions.
        The tree is constructed using the clasic binary search tree data structure, where each node represents 
        a split in the data along one of the three dimensions, where each
        node in the tree represents a split in the data along one of the three dimensions.
        Additionally, each node also contains a 2D range tree of the data points that fall within its
        region, to allow for efficient searches along the other two dimensions.

    """

    def __init__(self, points, axis=0):
        """
            Initializes a 3D range tree with the given list of points. The tree is balanced based on the x-coordinates of
            the points by default, but the axis can be changed , by setting the axis parameter to 0.
            
            Parameters:
            - points (List[Tuple[int, int, int]]): A list of (x, y, z) tuples representing the points in the tree.
            - axis (int): The axis to use for the initial split (default: 0, which corresponds to the x-axis)

        """

        self.axis = axis
        self.root = self._build_tree(points)

    def _build_tree(self, points):
        """
            Builds the 3D range tree recursively by dividing the input points into left and right subsets,
            according to the median of the x-coordinates of the points.

            This method is called during initialization and should not be called directly.
            
            Parameters:
            - points (List[Tuple[int, int, int]]): A list of (x, y, z) tuples representing the points in the tree.
            
            Returns:
            - Node: The root node of the tree.
        """

        if not points:
            return None

        if len(points) == 2:
            return Node(value=points[0], y_tree=RangeTree2D(points, axis=1))

        # Sort by x coord
        points.sort(key=lambda point: point[self.axis])
     
        median = len(points) // 2

        left_points = points[:median]

        right_points = points[median+1:]

        # In RangeTree3D
        left = RangeTree3D(left_points, axis=self.axis) if left_points else None
    
        right = RangeTree3D(right_points, axis=self.axis) if right_points else None

        return Node(left=left, right=right, value=points[median], y_tree=RangeTree2D(points, axis=1))

    def range_search(self, x_range, y_range, z_range):
        """
            Performs a range search on the 3D range tree, returning all points that fall within the given x-range.
            The search starts at the root of the tree and recursively traverses the left and right subtrees,
            depending on the location of the query range relative to the current node. 
        
            Parameters:
            - x_range (Tuple[int, int]): A tuple representing the x-range of the query, in the form (x_min, x_max).
            - y_range (Tuple[int, int]): A tuple representing the y-range of the query, in the form (y_min, y_max).
            - z_range (Tuple[int, int]): A tuple representing the z-range of the query, in the form (z_min, z_max).
            
            Returns:
            - List[Tuple[int, int, int]]: A list of (x, y, z) tuples representing the points in the tree that fall within
            the given x-range, y-range, and z-range.
        """
        if self.root is None: return []

        values = []
        if x_range[0] <= self.root.value[self.axis][0]<= x_range[1]:
            # Use the 2D range tree at the current node to filter the points based on the y and z ranges
            # Return only the points in the y_tree that fall within the y and z ranges of the query
            return [point for point in self.root.y_tree.range_search(y_range , z_range)  if x_range[0] <= point[0][0] <= x_range[1] and y_range[0] <= int(point[1]) <= y_range[1] ]

        # Traverse the left and right subtrees based on the location of the query range relative to the current node    
        if x_range[0] > self.root.value[self.axis]:
            if self.root.right:
                values += self.root.right.range_search(x_range, y_range, z_range)
        elif x_range[1] < self.root.value[self.axis]:
            if self.root.left:
                values += self.root.left.range_search(x_range, y_range, z_range)

        return values

def main():

    # Check if the correct number of command-line arguments are provided
    if len(sys.argv) != 4:
        print(
            "Usage: python script_name.py <surname_range> <awards_threshold> <dblp_range>\nExample: python range_tree.py A-T 1 20-1000\n"
        )
        return
    
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
            points.append((surname, awards, dblp_record ,education))


    # Displaying the list of points
    pp = pprint.PrettyPrinter(indent=4)
    start_time_total=time.time()

    # For Testing only
    """print("Points:")
    pp.pprint(points)"""


    """-------Range Tree Construction------------"""

    start_time = time.time()
    RangeTree = RangeTree3D(points)
    end_time = time.time()
    build_time = end_time - start_time

    # For Testing only
    #print(f"\n3D Tree ({len(points)} entries):\n")
    #pp.pprint(kd_tree)


    """-------Range Tree Search---------------"""

    # Parse command-line arguments
    surname_range = tuple(sys.argv[1].split("-"))
    awards_threshold = int(sys.argv[2])
    dblp_range = tuple(map(int, sys.argv[3].split("-")))
    start_time = time.time()
    search_results = RangeTree.range_search(surname_range, (awards_threshold , float("inf")), dblp_range)
    end_time = time.time()
    search_time = end_time - start_time

  # Print the points found within the query range
    print("Points within 3D range:")
    for point_3d in search_results:
        print(point_3d)

    print(len(search_results))
    # pp.pprint(search_results)

    """-------LSH Similarity Queries------------"""

    # LSH Similarity Queries
    # Create the educations list
    educations = []

    for result in search_results:
        educations.append(result[3])  # Education string is at position 3

    simil_thresh = 0.9
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

    print(f"\nNumber of scientists in the result: {len(search_results)}") 
    # Print execution time results
    print("\nExecution Time Results:")
    print(f"\nBuild Time: {build_time} seconds")
    print(f"Search Time: {search_time} seconds")
    print(f"LSH Time: {lsh_time} seconds")
    print(f"Total Time: {total_time} seconds")

if __name__ == "__main__":
    main()  
   