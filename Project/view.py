import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Sample DataFrame
data = {
    'Stock': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'FB'],
    'Shares': [50, 30, 40, 20, 60],
    'Price': [150.25, 2723.87, 289.20, 3326.13, 261.56]
}
df = pd.DataFrame(data)

# Create the main window
root = tk.Tk()
root.title('Portfolio GUI')

# Create a canvas for scrolling functionality
canvas = tk.Canvas(root)
canvas.grid(row=0, column=0, sticky='nsew')

# Enable two-finger scrolling on Mac trackpad
def on_mousewheel(event):
    canvas.yview_scroll(-1*(event.delta), "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)

# Create a scrollbar attached to the canvas
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.grid(row=0, column=1, sticky='ns')
canvas.configure(yscrollcommand=scrollbar.set)

# Frame inside the canvas
frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor='nw')

# Function to update the canvas's scrollregion after widgets change
def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox('all'))
frame.bind('<Configure>', on_configure)

# Display the DataFrame in a Treeview
tree = ttk.Treeview(frame, columns=list(df.columns), show='headings')
for column in df.columns:
    tree.heading(column, text=column)
    tree.column(column, width=100)

tree.pack(fill='both', expand=True)
for _, row in df.iterrows():
    tree.insert('', 'end', values=tuple(row))

# Create a dedicated frame for the matplotlib plot with a specified size
plot_frame = ttk.Frame(frame, width=550, height=350)  # Increased frame height
plot_frame.pack_propagate(0)  # Don't let the plot expand beyond the frame size
plot_frame.pack(fill='both', padx=10, pady=10)

# Embed a Matplotlib plot with adjusted size
fig, ax = plt.subplots(figsize=(6.5, 4.5))  # Slightly increased figsize again

df.plot(kind='bar', x='Stock', y='Price', ax=ax)
ax.set_title('Stock Prices')
ax.set_ylabel('Price ($)')
ax.set_xticklabels(df['Stock'], rotation=45)  # Rotated x-axis labels

# Modify the tight_layout padding again
fig.tight_layout(pad=3.0, h_pad=1.0, w_pad=1.0, rect=[0, 0.1, 1, 1])  
# Added rect to adjust the overall positioning of the plot within the figure

canvas_plot = FigureCanvasTkAgg(fig, master=plot_frame)
canvas_plot.draw()
canvas_plot.get_tk_widget().pack(fill='both', expand=True)


# Configure grid weights
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()
