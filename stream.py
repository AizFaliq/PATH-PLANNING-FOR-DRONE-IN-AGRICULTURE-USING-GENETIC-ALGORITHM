import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Title for the Streamlit app
st.title("Streamlit with Matplotlib Plot")

# Sidebar input for user interaction
st.sidebar.header("Plot Configuration")

graph_type = st.sidebar.selectbox(
    "Select the type of graph:",
    ("Sine Wave", "Cosine Wave")
)

frequency = st.sidebar.slider("Frequency:", 1, 20, 5)
amplitude = st.sidebar.slider("Amplitude:", 1, 10, 1)

# Generate data based on user input
x = np.linspace(0, 2 * np.pi, 500)
if graph_type == "Sine Wave":
    y = amplitude * np.sin(frequency * x)
else:
    y = amplitude * np.cos(frequency * x)

# Create a Matplotlib figure
fig, ax = plt.subplots()
ax.plot(x, y, label=f"{graph_type} (Frequency: {frequency}, Amplitude: {amplitude})")
ax.set_title("Generated Plot")
ax.set_xlabel("x-axis")
ax.set_ylabel("y-axis")
ax.legend()

# Display the Matplotlib figure in Streamlit
st.pyplot(fig)

# Add a text section
st.markdown(
    """
    ## About
    This app demonstrates how to integrate Matplotlib with Streamlit to create interactive plots.
    Use the sidebar to modify the graph type, frequency, and amplitude.
    """
)
