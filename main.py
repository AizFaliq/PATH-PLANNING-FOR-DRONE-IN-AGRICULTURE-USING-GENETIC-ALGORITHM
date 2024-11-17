import math
import random
import matplotlib.pyplot as plt
import GA

from functools import partial
from shapely import wkt
from shapely.geometry import Point, Polygon
from pyproj import Transformer
from matplotlib.animation import FuncAnimation

#|------------------------------------------------------------------------------------------------------------------------------------

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


#|------------------------------------------------------------------------------------------------------------------------------------

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


#|------------------------------------------------------------------------------------------------------------------------------------
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

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Define a function to handle mouse click events
def on_click(event, gen_circle, patch):
    # Check if the click is within the plot area

    global selected_circle

    if event.inaxes:
        # Get x and y coordinates of the click
        x, y = event.xdata, event.ydata
        click_point = Point(x,y)
        print(f"Clicked at: x={x}, y={y}")
        
        # Iterate through circles and update color based on click
        for i, circle in enumerate(gen_circle):
            circle_shape = Point(circle["center"]).buffer(circle["radius"])
            
            # Toggle "is_tree" status based on click position
            if circle_shape.contains(click_point):
                circle["is_tree"] = not circle["is_tree"]  # Toggle status
                if circle["is_tree"]:
                    # Add to selected_circle if `is_tree` is now True
                    if circle not in selected_circle:
                        selected_circle.append(circle)
                        print(f"Added circle: {circle}")
                else:
                    # Remove from selected_circle if `is_tree` is now False
                    if circle in selected_circle:
                        selected_circle.remove(circle)
                        print(f"Removed circle: {circle}")
            
            # Update color based on the updated "is_tree" status
            new_color = 'red' if circle["is_tree"] else 'green'
            patch[i].set_facecolor(new_color)  # Modify existing patch color

        plt.draw()  # Redraw plot to apply color changes
    
    return selected_circle

        
        # Optionally, display the click position on the plot
        # plt.plot(x, y, 'ro')  # red dot for clicked point
        # plt.draw()  # update the plot to show the point




#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# global variable

ax = ''
fig = ''
radius = 0
polygon = ''
x_limits = ''
y_limits = ''
node = ''
circle_within = ''
shifted_polygon = ''
selected_circle = []



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

print("System Start ------------------------------------------------------------------------")

# User input radius
radius = 10
print("Circle radius : ", radius)

# read file
with open("mapWKTfile.txt", "r") as file:
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

# Plot the shifted polygon in the all-positive quadrant
fig, ax = plt.subplots()
ax.plot(shifted_x, shifted_y, color='blue', linewidth=2, label='Polygon')
ax.fill(shifted_x, shifted_y, color='lightblue', alpha=0.5)  # Fill the polygon with color

# Plot the centroid
ax.plot(centroid_x, centroid_y, 'ro', label='Centroid')  # Red dot for centroid

# Set the axis limits based on the bounding box and padding
padding = 5  # meters
ax.set_xlim(0, max(shifted_x) + padding)
ax.set_ylim(0, max(shifted_y) + padding)

x_limits = ax.get_xlim()
y_limits = ax.get_ylim()

# Print the x and y axis limits
print("X-axis limits:", ax.get_xlim())
print("Y-axis limits:", ax.get_ylim())

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


# Correct use of partial to connect the function
click_callback = partial(on_click, gen_circle = circle_in, patch = patch)
fig.canvas.mpl_connect('button_press_event', click_callback)

# Add title, labels, and grid
ax.set_title("Polygon with Centroid and Circles in Positive Quadrant")
ax.set_xlabel("X (meters)")
ax.set_ylabel("Y (meters)")
ax.grid(True)
ax.legend()
ax.axis('equal')
plt.show()


circle_for_GA = {}
for j, item in enumerate(selected_circle, start=0):
    item_coor_x = item["center"][0]
    item_coor_y = item["center"][1]
    route_name = f"route {j + 1}"  # or any custom name
    circle_for_GA[route_name] = {'latitude': item_coor_x, 'longitude': item_coor_y}

print(circle_for_GA)
movement_coordinates = GA.GA(circle_for_GA)
print("Check final route : ", movement_coordinates)



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Second Plot: Add Routes
fig2, ax2 = plt.subplots()
ax2.plot(shifted_x, shifted_y, color='blue', linewidth=2, label='Polygon')
ax2.fill(shifted_x, shifted_y, color='lightblue', alpha=0.5)  # Fill the polygon with color

# Plot the centroid
ax2.plot(centroid_x, centroid_y, 'ro', label='Centroid')  # Red dot for centroid

# Set the axis limits
ax2.set_xlim(0, max(shifted_x) + padding)
ax2.set_ylim(0, max(shifted_y) + padding)

# Plot the circles
for circle in circle_in:
    if circle["is_tree"]:
        circle_plot = plt.Circle(circle["center"], circle["radius"], color='red')
    else:
        circle_plot = plt.Circle(circle["center"], circle["radius"], color='green')
    ax2.add_patch(circle_plot)


# Extract route coordinates
route_x = [coord[0] for coord in movement_coordinates]  # Longitude as X
route_y = [coord[1] for coord in movement_coordinates]  # Latitude as Y

print("route x ", route_x)
print("route y ", route_y)
# Plot routes
ax2.scatter(route_x, route_y, color='purple', label='Route Points', zorder=5)
ax2.plot(route_x, route_y, color='orange', linestyle='-', label='Route Path', zorder=4)

# Add labels, title, and grid
ax2.set_title("Polygon with Centroid, Circles, and Routes")
ax2.set_xlabel("X (meters)")
ax2.set_ylabel("Y (meters)")
ax2.grid(True)
ax2.legend()
ax2.axis('equal')

# Show the second plot
plt.show()


