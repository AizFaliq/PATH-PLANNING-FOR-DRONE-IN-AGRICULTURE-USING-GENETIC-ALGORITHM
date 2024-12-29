import math
import random
import matplotlib.pyplot as plt
import GA

from functools import partial
from shapely import wkt
from shapely.geometry import Point, Polygon
from pyproj import Transformer
from matplotlib.animation import FuncAnimation


# Function to set centre for each line
def genCentre(centroid_x, centroid_y, circleRad, y_limits):

    currentXNode = centroid_x
    currentYNode = centroid_y
    reachxlimit = False
    reachylimit = False
    upperYlimit = False
    lowerYlimit = False
    circleNum = 0
    circle = []
    print("polygon_limit", y_limits[1])

    # calculate height in-between circles
    circleHorizontal = math.sqrt(3) * circleRad
    print("Height between circles :",circleHorizontal)

    # initiate loop for creating upper and lower center node
    while not (reachxlimit or reachylimit):
        
        # adding new node
        node_to_check = (currentXNode,currentYNode)
        print("Current check node :", node_to_check)

        # Moving node either right or left
        if circleNum % 2 != 1 and circleNum != 1:
            currentXNode += circleRad
        else:
            currentXNode -= circleRad

        # Move to the top
        if not upperYlimit:  
            currentYNode = currentYNode + circleHorizontal
            if currentYNode > y_limits[1]:  
                upperYlimit = True 
                currentYNode = centroid_y
                currentXNode = centroid_x
                circleNum = 0
            elif node_to_check not in circle:
                circle.append(node_to_check)

        # Move to the bottom
        elif not lowerYlimit :  
            currentYNode = currentYNode - circleHorizontal
            if currentYNode < y_limits[0]:  
                lowerYlimit = True    
            elif node_to_check not in circle:
                print("Current check node :", node_to_check)
                circle.append(node_to_check)

        # Check if both reached limits
        if upperYlimit and lowerYlimit:
            reachylimit = True  

        print("Upper limit :", upperYlimit)
        print("Lower limit :",lowerYlimit)
        circleNum+=1
    
    print("Circle row : ", len(circle))
    print("Generating center for each line --------------------")
    for center in circle:
        print(center)

    return circle

# Function to generate a line of circle
def genCircleLine(centroid_x, centroid_y, circleRad):

    # Initialize flags and positions
    reachxlimit = False
    reachylimit = False
    currentXNode = centroid_x
    currentYNode = centroid_y
    circle_data = []
    rightlimit = False
    leftlimit = False

    while not (reachxlimit or reachylimit):
        circle = {"center": (currentXNode, currentYNode), "radius": circleRad, "is_tree": False}

        # Move to the right
        if not rightlimit:  
            rightXNode = currentXNode + circleRad * 2
            currentXNode = rightXNode
            if rightXNode > x_limits[1]:  
                rightlimit = True  
                currentXNode = centroid_x  
            elif circle not in circle_data:
                circle_data.append(circle)

        # Move to the left
        elif not leftlimit: 
            leftXNode = currentXNode - circleRad * 2
            currentXNode = leftXNode
            if leftXNode < x_limits[0]: 
                leftlimit = True  
                currentXNode = centroid_x  
            elif circle not in circle_data:
                circle_data.append(circle)

        # Check if both limits have been reached
        if rightlimit and leftlimit:
            reachxlimit = True  

    return circle_data

# Function to remove outer circles
def removeOuterCircle(centre_points, shifted_polygon):
    # Iterate over each set in centre_points
    circle_in = []
    for point_set in centre_points:
        # Extract x and y from the single element in the set
        (x, y) = (point_set) # Assumes each set has only one (x, y) tuple
        
        # Create the circle shape centered at (x, y) with the given radius
        circle_shape = Point((x, y)).buffer(radius)
        circle = genCircleLine(x, y, radius)

        for circle in circle:
            circle_shape = Point(circle["center"]).buffer(radius)
            print(circle)

            if shifted_polygon.contains(circle_shape):
                circle_in.append(circle)
    
    return circle_in
    

#|------------------------------------------------------------------------------------------------------------------

radius = 5

# Read file containing WKT
with open("triangle.txt", "r") as file:
    wkt_data = file.read()

# Set transformer from WGS84 to UTM Zone 48N
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32647", always_xy=True)

# Load the polygon from WKT
polygon = wkt.loads(wkt_data)
print(polygon)

# Transform each coordinate in the polygon to UTM (meters)
utm_points = [transformer.transform(lon, lat) for lon, lat in polygon.exterior.coords]
utm_polygon = Polygon(utm_points)

# Find minimum x and y to shift polygon into positive quadrant
min_x, min_y = min(x for x, y in utm_points), min(y for x, y in utm_points)

# Shift the polygon points to ensure all coordinates are positive
shifted_points = [(x - min_x, y - min_y) for x, y in utm_points]
shifted_x, shifted_y = zip(*shifted_points)

shifted_polygon = Polygon(shifted_points)

# Calculate the centroid of the polygon and shift it into the positive quadrant
centroid = utm_polygon.centroid
centroid_x, centroid_y = centroid.x - min_x, centroid.y - min_y





















# Print the x and y value of the center 
print("Center x-axis : ", centroid_x)
print("Center y-axis : ", centroid_y)


# Print the transformed polygon (optional)
print("Shifted Polygon (UTM):", shifted_polygon)

# Plotting the transformed polygon in UTM
fig, ax = plt.subplots()

# Set the axis limits based on the bounding box and padding
padding = 5  # meters
ax.set_xlim(0, max(shifted_x) + padding)
ax.set_ylim(0, max(shifted_y) + padding)

x_limits = ax.get_xlim()
y_limits = ax.get_ylim()

# Generate center points
node = genCentre(centroid_x, centroid_y, radius, y_limits)
circle_in = removeOuterCircle(node, shifted_polygon)
print("Number of generated circle in poly : ", len(circle_in))

# Plot the circles
patch = []
for circle in circle_in:
    circle_plot = plt.Circle(circle["center"], circle["radius"], color='green')
    ax.add_patch(circle_plot)
    patch.append(circle_plot)
    

# Plot the centroid
ax.plot(centroid_x, centroid_y, 'ro', label='Centroid')  # Red dot for centroid

# Extract UTM coordinates for plotting
x, y = shifted_polygon.exterior.xy

# Plot the transformed polygon
ax.fill(x, y, alpha=0.5, fc='blue', label='Polygon')

# If there are any holes in the polygon, plot them
for interior in shifted_polygon.interiors:
    ix, iy = interior.xy
    ax.fill(ix, iy, alpha=0.5, fc='red', label='Hole')

# Add labels and legend
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")
ax.legend()

# Show the plot
plt.show()