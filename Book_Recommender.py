import numpy as np
import pandas as pd
import joblib
import os
import tkinter as tk
import customtkinter as ctk
import ctypes
from Model_Creation import creating_data
from PIL import ImageTk, Image
import requests
import tempfile


# Set DPI awareness
ctypes.windll.shcore.SetProcessDpiAwareness(1)

# Get current working directory
current_dir = os.getcwd()

# Check if the model is already created
if not os.path.isfile(current_dir + '/Data/KNN_model.pkl') or (
    not os.path.isfile(current_dir + '/Data/Cleaned_Data.csv')):
    print("Creating model...")
    creating_data()
    print("Model created")
else:
    print("Model loaded")

# Load the model and the data
neigh = joblib.load('Data/KNN_model.pkl')
piv = pd.read_csv('Data/Cleaned_Data.csv', index_col=0)

# Get the titles and initialize the book recommendations variable
titles = list(piv.index.values)
book_recs = None


# Define a function to easily get the index of a book
def title_to_index(title):
    return piv.values[titles.index(title), :]


# Define a function to easily get the title of a book
def index_to_title(num):
    return titles[num]


# Set the theme and appearance mode
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


# Define the main app class
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Book Recommender")
        self.geometry("500x500")
        self.resizable(False, False)
        
        # Configure grid
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        # Initiate the Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, columnspan=8, rowspan=3, padx=(20, 15), pady=(15, 15), sticky="nsew")
        

        # Define a function to search for matches
        def search_matches(search_term):
            matches = [x for x in titles if search_term.lower() in x.lower()]
            return matches


        # Define a function to handle button clicks
        def handle_click(event=None):
            # Get the search term from the entry widget
            search_term = entry.get()

            # Search for matches based on the search term
            matches = search_matches(search_term)

            # Display the matches in the listbox widget
            listbox.delete(0, tk.END)
            for index in matches:
                listbox.insert(tk.END, index)


        # Define a function to handle selection changes in the listbox widget
        def handle_select(event):
            # Get the selected index from the listbox widget
            if listbox.curselection() == ():
                return
            #selected_index = listbox.get(listbox.curselection())

        
        # Apply the KNN model to the selected book and return the top 5 recommendations
        def get_best_match():
            if listbox.curselection() == ():
                return
            
            # Get the selected book from the listbox widget
            selected_index = listbox.get(listbox.curselection())
            dist, inds = neigh.kneighbors(np.reshape(title_to_index(
                selected_index), [1, -1]), len(titles), True)
            results_listbox.delete(0, tk.END)

            # Display the top 5 recommendations in the listbox widget
            for i in range(5, 0, -1):
                results_listbox.insert(tk.END, f"{round(dist[0, i] * 100, 2)}%: {titles[inds[0, i]]}")      
            return book_recs
        

        # Create a new window to display the image of the selected book
        def display_image_from_url():
            url = get_book_url()
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }
            
            response = requests.get(url, headers=headers)
            image_data = response.content

            root = tk.Toplevel()
            root.title("Image Viewer")

            # Save the image data to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(image_data)

            # Open the temporary file as a PIL image
            image = Image.open(temp_file.name)

            # Resize the image if necessary
            max_width = root.winfo_screenwidth() - 100
            max_height = root.winfo_screenheight() - 100
            image.thumbnail((max_width, max_height))

            # Create a Tkinter-compatible image object
            tk_image = ImageTk.PhotoImage(image)

            # Create a label widget to display the image
            label = tk.Label(root)
            label.pack()

            # Assign the image to the label widget
            label.image = tk_image

            # Set the image on the label
            label.config(image=tk_image)

            root.mainloop()
        

        # Get the URL of the selected book
        def get_book_url():
            if results_listbox.curselection() == ():
                return 'https://drupal.nypl.org/sites-drupal/default/files/blogs/J5LVHEL.jpg'
            selected_index = results_listbox.get(results_listbox.curselection())
            df_books = pd.read_csv(
            "Books/BX-Books.csv",
            encoding = "ISO-8859-1",
            sep=";",
            header=0,
            names=['Title', "URL"],
            usecols=[1, 7],
            dtype={'Title': 'str', "URL": 'str'})
            book_url = df_books[df_books["Title"] == selected_index.split(": ")[1]]['URL'].iloc[0]
            return book_url


        # Create the search label and entry widget
        search_label = ctk.CTkLabel(self.main_frame, text='Title: ')
        search_label.grid(row=0, column=0, sticky=tk.W)
        entry = ctk.CTkEntry(self.main_frame)
        entry.grid(row=0, column=1, columnspan=7, sticky="ew")
        
        # Create the listbox widget and scrollbar
        listbox = tk.Listbox(self.main_frame, width=72)
        listbox.grid(row=1, column=0, columnspan=8, sticky=tk.W + tk.E)

        listbox_scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL)
        listbox_scrollbar.grid(row=1, column=7, sticky=tk.E + tk.N + tk.S)
        listbox_scrollbar.config(command=listbox.yview)

        listbox.config(yscrollcommand=listbox_scrollbar.set)

        # Create the search button, best match label, and results listbox
        button = tk.Button(self.main_frame, text='Search for best match', command=get_best_match)
        button.grid(row=2, column=0, columnspan=8, sticky=tk.W + tk.E)
        
        best_match = ctk.CTkLabel(self.main_frame, text='Best Match: ')
        best_match.grid(row=3, column=0, sticky=tk.W)

        results_listbox = tk.Listbox(self.main_frame, width=72)
        results_listbox.grid(row=4, column=0, columnspan=8, sticky=tk.W + tk.E)

        # Create a show image button
        show_image_button = tk.Button(self.main_frame, text="Show Image", command=display_image_from_url)
        show_image_button.grid(row=5, column=0, columnspan=8, sticky=tk.W + tk.E)

        # Bind the selection event to the listbox widget
        listbox.bind('<<ListboxSelect>>', handle_select)
        listbox.bind('<<ListboxSelect>>', handle_select)
        listbox.bind('<Double-1>', get_best_match)
        entry.bind("<KeyRelease>", handle_click)

        # Call the handle_click() function to initiate the search
        handle_click()


if __name__ == '__main__':
    app = App()
    app.mainloop()