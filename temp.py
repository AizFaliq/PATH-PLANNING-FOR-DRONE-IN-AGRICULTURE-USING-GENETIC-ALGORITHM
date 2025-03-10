
if __name__ == "__main__":
    

    import math
    import random
    import matplotlib.pyplot as plt
    import GA
    import customtkinter as ctk
    import sys

    from functools import partial
    from shapely import wkt
    from shapely.geometry import Point, Polygon
    from pyproj import Transformer
    from matplotlib.animation import FuncAnimation
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from config import map_shape_selected, spray_size_selected

    # Initialize CustomTkinter
    app = ctk.CTk()
    app.title("Drone Path Planning")
    app.geometry("1200x600")
    plt.ioff()

    
    # Initialize CustomTkinter
    app = ctk.CTk()
    app.title("Drone Path Planning")
    app.geometry("1200x600")
    plt.ioff()

    # Globlal Variable

    selected_circle = []
    start_node = None
    end_node = None
    mode = "toggle_trees"  
    circle_data = ''
    path = None
    map_shape = map_shape_selected  
    spray_size = spray_size_selected 
    wkt_data = ""
    canvas = ""
    patch = ""
    x_limits = []
    radius = ""
    circle_in = ""


    def main():
        global shape, spray_radius  # Declare that we are using the global variables

        # Ensure correct number of arguments are passed
        if len(sys.argv) != 3:
            print("Usage: python main.py <shape> <spray_radius>")
            return
        
        # Read values from command line
        shape = sys.argv[1]
        spray_radius_input = sys.argv[2].lower()  # Convert to lowercase for consistency
        
        # Assign spray radius based on input
        if spray_radius_input == "small":
            spray_radius = "small"
        elif spray_radius_input == "medium":
            spray_radius = "medium"
        elif spray_radius_input == "large":
            spray_radius = "large"
        else:
            print("Invalid spray radius. Please choose 'small', 'medium', or 'large'.")
            return

        # Use the received values in your application
        print(f"Selected Shape: {shape}")
        print(f"Spray Radius: {spray_radius}")

        # Now you can use 'shape' and 'spray_radius' in your main logic
        # Example: Initialize your graph generation logic with these values

    def restart_app():
        global app
        app.destroy()  # Close current window
        app = ctk.CTk()  # Create a new app window
        app.title("New Instance")
        app.mainloop()

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
        global x_limits
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
        

    # Function to toggle tree status
    def on_click(event, gen_circle, patch):
        global selected_circle, mode

        if mode != "toggle_trees":
            return  # Only act in "toggle_trees" mode

        if event.inaxes:
            x, y = event.xdata, event.ydata
            click_point = Point(x, y)
            print(f"Clicked at: x={x}, y={y}")

            # Iterate through circles and toggle "is_tree"
            for i, circle in enumerate(gen_circle):
                circle_shape = Point(circle["center"]).buffer(circle["radius"])

                if circle_shape.contains(click_point):
                    # Toggle tree status
                    circle["is_tree"] = not circle["is_tree"]

                    # Update selected_circle list
                    if circle["is_tree"]:
                        if circle not in selected_circle:
                            selected_circle.append(circle)
                            print(f"Added circle: {circle}")
                    else:
                        if circle in selected_circle:
                            selected_circle.remove(circle)
                            print(f"Removed circle: {circle}")

                    # Update patch color
                    new_color = '#118B50' if circle["is_tree"] else 'green'
                    patch[i].set_facecolor(new_color)

            canvas.draw()  # Update the plot

    # Function to select start and end nodes
    def select_nodes(event, gen_circle, patch):
        global start_node, end_node, mode

        if mode != "select_nodes":
            return  # Only act in "select_nodes" mode

        if event.inaxes:
            x, y = event.xdata, event.ydata
            click_point = Point(x, y)
            print(f"Clicked at: x={x}, y={y}")

            # Iterate through circles to identify the clicked node
            for i, circle in enumerate(gen_circle):
                circle_shape = Point(circle["center"]).buffer(circle["radius"])

                if circle_shape.contains(click_point):
                    if start_node is None:
                        start_node = circle
                        selected_circle.append(circle)
                        patch[i].set_facecolor('#789DBC')  # Highlight start node
                        print(f"Start node selected: {circle}")
                    elif end_node is None:
                        end_node = circle
                        selected_circle.append(circle)
                        patch[i].set_facecolor('#789DBC')  # Highlight end node
                        print(f"End node selected: {circle}")
                    else:
                        print("Both nodes already selected. Reset to select again.")

                    canvas.draw()  # Update the plot
                    break

    # Function to reset the graph
    def reset_all():
        global start_node, end_node, selected_circle

        start_node = None
        end_node = None
        selected_circle.clear()

        # Reset circle colors
        for i, circle in enumerate(circle_in):
            circle["is_tree"] = False
            patch[i].set_edgecolor('#118B50')  
            patch[i].set_facecolor('none')   
            patch[i].set_linewidth(2)  

        print("Reset selection!")
        canvas.draw()  # Redraw the plot

    # Function to confirm and pass data to the GA function
    def confirm_selection():
        global start_node, end_node, selected_circle, path

        # Ensure start and end nodes are selected
        if start_node is None or end_node is None:
            print("Please select both a start and an end node before confirming.")
            return
        

        # insert circle_in for all circles, or selected_circle for selected circles
        circle_for_GA = {}
        for j, item in enumerate(selected_circle, start=0):
            item_coor_x = item["center"][0]
            item_coor_y = item["center"][1]
            route_name = f"route {j + 1}"  # or any custom name
            circle_for_GA[route_name] = {'latitude': item_coor_x, 'longitude': item_coor_y}
            if item["center"][0] == start_node["center"][0] and item["center"][1] == start_node["center"][1]:
                starting_node = route_name
            elif item["center"][0] == end_node["center"][0] and item["center"][1] == end_node["center"][1]:
                ending_node = route_name

        print("start/end node")
        print(starting_node)
        print(ending_node)
        print(circle_for_GA)
        movement_coordinates = GA.GA(circle_for_GA, starting_node, ending_node)

        #Second Plot: Add Routes
        fig2, ax2 = plt.subplots()
        ax2.plot(shifted_x, shifted_y, color='blue', linewidth=2, label='Polygon')
        ax2.fill(shifted_x, shifted_y, color='lightblue', alpha=0.5)  # Fill the polygon with color

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

        # Embed the graph in the Tkinter container
        canvas = FigureCanvasTkAgg(fig2, master=section3)
        canvas.get_tk_widget().pack()
        canvas.draw()

    # Function to switch modes
    def set_mode(new_mode):
        global mode
        mode = new_mode
        print(f"Mode set to: {mode}")

    # Function to change button appearance on hover
    def on_hover(button):
        button.configure(fg_color="white", text_color="#2E8B57")  # White background with green text on hover

    def on_leave(button):
        button.configure(fg_color="#2E8B57", text_color="white")  # Leaf green background with white text when not hovered

    # Function to handle shape selection (for first section)
    def set_map_shape_and_action(shape):
        global map_shape
        
        # Add unique behavior for each shape
        if shape == "Rectangle":
            map_shape = "Rectangle"
        elif shape == "Triangle":
            map_shape = "Triangle"
        elif shape == "Irregular":
            map_shape = "Irregular"
        
        print("Current shape:")
        print(shape)


    # Function to handle spray selection (for second section)
    def on_spray_selected(size):
        global spray_size
        spray_size = size  

        print("Current spray size:")
        print(spray_size)



    #|------------------------------------------------------------------------------------------------------------------

    

    # Scrollable main frame
    main_frame = ctk.CTkScrollableFrame(app, corner_radius=0)
    main_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

    # Title section in main_frame
    title_section = ctk.CTkFrame(main_frame, height=100, corner_radius=0)
    title_section.grid(row=0, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
    ctk.CTkLabel(title_section, text="Drone Path Planning", font=("Arial", 24, "bold")).pack(pady=20)

    # Section 1 in main frame (with graph placeholder)
    section1 = ctk.CTkFrame(main_frame, height=250, corner_radius=0)
    section1.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")


    if map_shape == "Rectangle":
        with open("rectangle.txt", "r") as file:
            wkt_data = file.read()
    elif map_shape == "Triangle":
        with open("triangle.txt", "r") as file:
            wkt_data = file.read()
    elif map_shape == "Irregular":
        with open("irregular.txt", "r") as file:
            wkt_data = file.read()
        
    if spray_size == "Small":
        radius = 2
    elif spray_size == "Medium":
        radius = 3
    elif spray_size == "Large":
        radius = 4


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
    fig.patch.set_facecolor("white")
    ax.set_facecolor('white')

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
        circle_plot = plt.Circle(circle["center"], circle["radius"], edgecolor='#118B50', facecolor='none',  linewidth=2)
        ax.add_patch(circle_plot)
        patch.append(circle_plot)

    # Extract UTM coordinates for plotting
    x, y = shifted_polygon.exterior.xy

    # Plot the transformed polygon
    ax.plot(shifted_x, shifted_y, color='#118B50', linewidth=2, label='Polygon')


    # Add labels and legend
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")
    ax.legend()





    canvas_width = 800
    canvas_height = int(9 / 16 * canvas_width)  # Calculate height for 16:9 ratio

    # Embed the graph into CustomTkinter
    canvas = FigureCanvasTkAgg(fig, master=section1)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side="top", pady=10, padx=10)
    canvas_widget.config(width=canvas_width, height=canvas_height)

    # Bind click events to the figure
    fig.canvas.mpl_connect('button_press_event', partial(on_click, gen_circle=circle_in, patch=patch))
    fig.canvas.mpl_connect('button_press_event', partial(select_nodes, gen_circle=circle_in, patch=patch))




    # Section 2 in main frame (with the buttons stacked vertically)
    section2 = ctk.CTkFrame(main_frame, height=250, corner_radius=0)
    section2.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
    ctk.CTkLabel(section2, text="Select Area and Start/End", font=("Arial", 18, "bold")).pack(pady=20)

    # Create an inner frame to use grid for the buttons
    buttons_frame = ctk.CTkFrame(section2)
    buttons_frame.pack(pady=10, fill="x")


    # Add buttons to switch modes and reset
    toggle_button = ctk.CTkButton(
        master=buttons_frame, text="Toggle Spray Area",
        command=lambda: set_mode("toggle_trees"),
        corner_radius=10, 
        height=40, 
        width=150, 
        fg_color="#2E8B57"
    )
    toggle_button.pack(side="top", pady=10)
    toggle_button.bind("<Enter>", lambda event, button=toggle_button: on_hover(toggle_button))  # On hover
    toggle_button.bind("<Leave>", lambda event, button=toggle_button: on_leave(toggle_button))  # On leave

    select_button = ctk.CTkButton(
        master=buttons_frame, text="Start/End",
        command=lambda: set_mode("select_nodes"),
        corner_radius=10, 
        height=40, 
        width=150, 
        fg_color="#2E8B57"
    )
    select_button.pack(side="top", pady=10)
    select_button.bind("<Enter>", lambda event, button=select_button: on_hover(select_button))  # On hover
    select_button.bind("<Leave>", lambda event, button=select_button: on_leave(select_button))  # On leave

    reset_button = ctk.CTkButton(
        master=buttons_frame, text="Reset",
        command=reset_all,
        corner_radius=10, 
        height=40, 
        width=150, 
        fg_color="#2E8B57"
    )
    reset_button.pack(side="top", pady=10)
    reset_button.bind("<Enter>", lambda event, button=reset_button: on_hover(reset_button))  # On hover
    reset_button.bind("<Leave>", lambda event, button=reset_button: on_leave(reset_button))  # On leave

    confirm_button = ctk.CTkButton(
        master=buttons_frame, text="Confirm",
        command=confirm_selection,
        corner_radius=10, 
        height=40, 
        width=150, 
        fg_color="#2E8B57"
    )
    confirm_button.pack(side="top", pady=10)
    confirm_button.bind("<Enter>", lambda event, button=confirm_button: on_hover(confirm_button))  # On hover
    confirm_button.bind("<Leave>", lambda event, button=confirm_button: on_leave(confirm_button))  # On leave

    # Section 3 in main frame (empty until action)
    section3 = ctk.CTkFrame(main_frame, height=250, corner_radius=0)
    section3.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

    # Section 3 content (empty initially)
    ctk.CTkLabel(section3, text="Section 3: Additional Graph", font=("Arial", 18, "bold")).pack(pady=10)


    app.mainloop()

