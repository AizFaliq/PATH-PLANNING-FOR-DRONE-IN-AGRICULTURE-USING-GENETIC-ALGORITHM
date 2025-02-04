import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk  
import matplotlib.pyplot as plt
import function as func
import numpy as np


map_shape = "Rectangle"  
spray_size = "Small"  

# Function to change button appearance on hover
def on_hover(button):
    button.configure(fg_color="white", text_color="#2E8B57")  # White background with green text on hover

def on_leave(button):
    button.configure(fg_color="#2E8B57", text_color="white")  # Leaf green background with white text when not hovered

# Function to handle shape selection (for first section)
def set_map_shape_and_action(shape):
    global map_shape
    map_shape = shape  
    print(f"Selected shape: {map_shape}")
    update_shape_label()
    update_graph()  

    # Add unique behavior for each shape
    if shape == "Rectangular":
        rectangular_function()
    elif shape == "Triangle":
        triangle_function()
    elif shape == "Irregular":
        irregular_function()

# Function to handle spray selection (for second section)
def on_spray_selected(size):
    global spray_size
    spray_size = size  
    print(f"Selected spray size: {spray_size}")

# Function to update the label in Section 1 based on the selected shape
def update_shape_label():
    shape_title_label.configure(text=f"Shape Selected: {map_shape}")

def update_graph():
    global map_shape, spray_size


    # Create figure for the graph using the function from the other file
    fig = func.create_map(map_shape, spray_size)  # Call the create_map function from another file

    # Embed the generated figure into the CTkinter window
    canvas = FigureCanvasTkAgg(fig, master=section1)  # Create a canvas with the Matplotlib figure
    canvas.draw()  # Draw the canvas

    # Pack the canvas into the section (this will add the new graph)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # Close the figure to avoid memory leaks
    plt.close(fig)


# Placeholder functions for different shapes
def rectangular_function():
    print("Rectangular shape selected - Additional function running.")

def triangle_function():
    print("Triangle shape selected - Additional function running.")

def irregular_function():
    print("Irregular shape selected - Additional function running.")

def select_tree():
    print("Select Tree button clicked")

def select_start_end():
    print("Select Start/End button clicked")

def reset():
    print("Reset button clicked")

def confirm():
    print("Confirm button clicked")

# Initialize the main window
app = ctk.CTk()
app.title("Drone Path Planning")
app.geometry("1200x600")

# Navigation frame (fixed width)
nav_frame = ctk.CTkFrame(app, width=250, corner_radius=0)
nav_frame.pack(side="left", fill="y", padx=10, pady=10)

# Section 1: Choose Shape
shape_label = ctk.CTkLabel(nav_frame, text="Choose Shape", font=("Arial", 18, "bold"))
shape_label.pack(pady=(20, 10))

shape_buttons = ["Rectangular", "Triangle", "Irregular"]
for btn in shape_buttons:
    button = ctk.CTkButton(nav_frame, text=btn, corner_radius=10, fg_color="#2E8B57")
    button.pack(pady=5, padx=20, fill="x")
    button.bind("<Enter>", lambda event, button=button: on_hover(button))  # On hover
    button.bind("<Leave>", lambda event, button=button: on_leave(button))  # On leave
    button.configure(command=lambda b=btn: set_map_shape_and_action(b))  # On button click

# Update button commands without creating new buttons
for widget in nav_frame.winfo_children():
    if isinstance(widget, ctk.CTkButton) and widget.cget("text") in shape_buttons:
        widget.configure(command=lambda b=widget.cget("text"): set_map_shape_and_action(b))

# Section 2: Select Spray Radius
radius_label = ctk.CTkLabel(nav_frame, text="Select Spray Radius", font=("Arial", 18, "bold"))
radius_label.pack(pady=(40, 10))

radius_buttons = ["Small", "Medium", "Large"]
for btn in radius_buttons:
    button = ctk.CTkButton(nav_frame, text=btn, corner_radius=10, fg_color="#2E8B57")
    button.pack(pady=5, padx=20, fill="x")
    button.bind("<Enter>", lambda event, button=button: on_hover(button))  # On hover
    button.bind("<Leave>", lambda event, button=button: on_leave(button))  # On leave
    button.configure(command=lambda b=btn: on_spray_selected(b))  # On button click

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

# Create the label dynamically so we can update it later
shape_title_label = ctk.CTkLabel(section1, text="Shape Selected: None", font=("Arial", 18, "bold"))
shape_title_label.pack(pady=20)

# Initial Graph in Section 1 (Default graph, not placeholder image)
update_graph()  # Call update_graph to show a default graph on window initialization

# Section 2 in main frame (with the buttons stacked vertically)
section2 = ctk.CTkFrame(main_frame, height=250, corner_radius=0)
section2.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
ctk.CTkLabel(section2, text="Section 2: Select Tree and Start/End", font=("Arial", 18, "bold")).pack(pady=20)

# Create an inner frame to use grid for the buttons
buttons_frame = ctk.CTkFrame(section2)
buttons_frame.pack(pady=10, fill="x")

# Add buttons inside the inner frame and arrange them vertically with better sizing
button_functions = [select_tree, select_start_end, reset, confirm]
button_labels = ["Select Tree", "Select Start/End", "Reset", "Confirm"]
for i, label in enumerate(button_labels):
    button = ctk.CTkButton(buttons_frame, text=label, corner_radius=10, height=40, width=150, fg_color="#2E8B57",
                           command=button_functions[i])
    button.pack(pady=10, fill="x")
    button.bind("<Enter>", lambda event, button=button: on_hover(button))  # On hover
    button.bind("<Leave>", lambda event, button=button: on_leave(button))  # On leave

# Section 3 in main frame (empty until action)
section3 = ctk.CTkFrame(main_frame, height=250, corner_radius=0)
section3.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

# Section 3 content (empty initially)
ctk.CTkLabel(section3, text="Section 3: Additional Graph", font=("Arial", 18, "bold")).pack(pady=10)

# Run the app
app.mainloop()
