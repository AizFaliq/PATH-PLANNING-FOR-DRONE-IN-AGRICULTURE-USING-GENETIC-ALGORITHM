import customtkinter as ctk
import subprocess

def main():
    ctk.set_appearance_mode("dark")  # Options: "dark", "light", "system"
    ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"
    
    # Create main window
    root = ctk.CTk()
    root.title("CustomTkinter Window")
    root.geometry("600x400")
    
    # Add a label
    label = ctk.CTkLabel(root, text="Welcome to CustomTkinter", font=("Arial", 18))
    label.pack(pady=20)
    
    # Add dropdown menus
    map_shape_var = ctk.StringVar(value="Select available map shape")
    map_shape_dropdown = ctk.CTkComboBox(root, values=["Triangle", "Rectangle", "Irregular"], variable=map_shape_var)
    map_shape_dropdown.pack(pady=10)
    
    spray_radius_var = ctk.StringVar(value="Select spray radius")
    spray_radius_dropdown = ctk.CTkComboBox(root, values=["Small", "Medium", "Large"], variable=spray_radius_var)
    spray_radius_dropdown.pack(pady=10)
    
    # Function to update config.py and execute temp.py
    def confirm_selection():
        # Update config.py with selected values
        with open('config.py', 'w') as f:
            f.write(f"map_shape_selected = '{map_shape_var.get()}'\n")
            f.write(f"spray_size_selected = '{spray_radius_var.get()}'\n")
        
        # Execute temp.py
        subprocess.run(['python', 'temp.py'])
    
    # Add a confirmation button
    confirm_button = ctk.CTkButton(root, text="Confirm", command=confirm_selection)
    confirm_button.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    main()
