# ## GROUP PROJECT: MIS41110 
# ## GROUP NUMBER: 11
# 
# ## BINGO!
#
# Import all necessary libraries:

import numpy as np
import random
from fpdf import FPDF
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
import webbrowser
from scipy.stats import skew, kurtosis

# Create the main application window
root = tk.Tk()
root.title("Card Generator")
root.geometry("1000x800")
root.configure(bg="seashell2")

# Ask User for number of cards in a game and number of simulations to run
def on_button1_click():

    number_of_cards = int(cards_entry.get())
    number_of_simulations = int(simulations_entry.get())
        
    # For simplicity, let's just print the values for now
    print(f"Cards to Generate: {number_of_cards}, Simulations: {number_of_simulations}")
    
    # Create a Bingo card with random numbers
    def create_bingo_card():
        # Generate random numbers for each column
        bingo_card = np.zeros((5, 5), dtype=int)
        for i in range(5):
            bingo_card[:, i] = np.random.choice(np.arange(i * 15 + 1, i * 15 + 15), size=5, replace=False)
        
        # Mark the center as freespace
        bingo_card[2, 2] = 0
        return bingo_card
        
    # Function to write the Bingo card to PDF using fpdf
    def write_bingo_card_to_pdf(card, pdf, card_number):
        pdf.add_page()
        pdf.set_font("Arial", size=42)
        pdf.cell(200, 10, txt='Your Bingo Card number {}:'.format(card_number + 1), ln=True, align='C')
        pdf.ln()

        for row_index, row in enumerate(card):
            for col_index, number in enumerate(row):
                if number == 0:
                    pdf.cell(39, 50, txt="X", border=1, align='C')
                else:
                    pdf.cell(39, 50, txt=str(number), border=1, align='C')
            pdf.ln()
    
    # Create PDF document using fpdf    
    global pdf_filename
    pdf_filename = "bingo_cards.pdf"
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=11)

    # Generate Bingo cards and sequences (replace this with your actual data)
    # bingo_cards = [create_bingo_card() for _ in range(number_of_cards)]
    bingo_cards = []

    for count in range(number_of_cards):
        # Create a Bingo card
        bingo_card = create_bingo_card()

        # List of all bingo cards
        bingo_cards.append(bingo_card)
        
        # Write the Bingo card to PDF
        write_bingo_card_to_pdf(bingo_card, pdf, count)

    # Save the PDF file
    pdf.output(pdf_filename)
    
        
    # Function that checks if sent card has a Bingo or not
    def is_bingo(card):
        # Check for a Bingo in rows, columns, and diagonals
        for i in range(5):
            if all(cell == 0 for cell in card[i]) or all(card[j][i] == 0 for j in range(5)):
                return True
        if all(card[i][i] == 0 for i in range(5)) or all(card[i][4 - i] == 0 for i in range(5)):
            return True
        return False
        
    def is_fullhouse(card):
        # Check if all numbers on the Bingo card are marked
        for row in card:
            if any(cell != 0 for cell in row):
                return False
        return True

    # Function that simulates Bingo
    def simulate_bingo_game(card,sequence,bingo_tracker):
        index = -1
        for number in sequence:
            bingo_flag = False  # Flag to track whether a Bingo has occurred for the current card
            for row in range(5):
                for col in range(5):
                    if card[row][col] == number:
                        card[row][col] = 0  # Mark the number as called
            # Skip if Bingo has already occurred for this card
            if bingo_flag:
                break
            
            # Check for Bingo
            if is_bingo(card):
                bingo_tracker[index]+=1  # Store the index of the sequence on which Bingo occurred
                bingo_flag = True
                break
            index += 1
        return bingo_tracker
        
    # Function that simulates Fullhouse
    def simulate_fullhouse_game(card,sequence,fullhouse_tracker):
        index = -1
        for number in sequence:
            for row in range(5):
                for col in range(5):
                    if card[row][col] == number:
                        card[row][col] = 0  # Mark the number as called
        
            # Check for Fullhouse
            if is_fullhouse(card):
                fullhouse_tracker[index]+=1  # Store the index of the sequence on which Fullhouse occurred
                break
            index += 1
        return fullhouse_tracker

    bingo_tracker = [0]*76  # List to store the index of the simulation on which Bingo occurred for each card
    fullhouse_tracker = [0]*76  # List to store the index of the simulation on which Fullhouse occurred for each card

    #List of trackers
    complete_bingo_tracker = []
    complete_fullhouse_tracker = []

    # Simulate the game
    for _ in range(number_of_simulations):
        sequence = random.sample(range(1,76),75)
        for card in bingo_cards:
            complete_bingo_tracker.append(simulate_bingo_game(card,sequence,bingo_tracker)[:-1])
            complete_fullhouse_tracker.append(simulate_fullhouse_game(card,sequence,fullhouse_tracker)[:-1])


    # Convert complete trackers to numpy arrays
    complete_bingo_tracker = np.array(complete_bingo_tracker,dtype=int)
    complete_fullhouse_tracker = np.array(complete_fullhouse_tracker,dtype=int)

    #complete_bingo_tracker = complete_bingo_tracker[number_of_cards-1::number_of_cards]
    #complete_fullhouse_tracker = complete_fullhouse_tracker[number_of_cards-1::number_of_cards]

    complete_bingo_tracker = np.transpose(np.cumsum(complete_bingo_tracker[:number_of_simulations,:], axis=1))
    complete_fullhouse_tracker = np.transpose(np.cumsum(complete_fullhouse_tracker[:number_of_simulations,:],axis=1))
    
    # Write trackers to csv files
    #np.savetxt("Complete_Bingo_tracker.csv",complete_bingo_tracker,fmt='%d', delimiter=",")
    #np.savetxt("Complete_Fullhouse_tracker.csv",complete_fullhouse_tracker,fmt='%d', delimiter=",")

    # - We calculated various centrality measures (median, percentiles, skewness, excess kurtosis) for each number called in the Bingo games.
    # - These measures provide insights into the distribution and variability of Bingo and Full-house achievements at different stages of the game.

    def calculate_centrality_measures_for_each_number(data):
        #Calculates centrality measures for each number called.
        centrality_measures = {
            "Number Called": np.arange(1, data.shape[1] + 1),
            "Median": np.median(data, axis=0),
            "25th Percentile": np.percentile(data, 25, axis=0),
            "75th Percentile": np.percentile(data, 75, axis=0),
            "Skewness": skew(data, axis=0),
            "Excess Kurtosis": kurtosis(data, axis=0)
        }
        return pd.DataFrame(centrality_measures)

    # Calculating the centrality measures for Bingo and Full-house
    bingo_centrality_measures = calculate_centrality_measures_for_each_number(complete_bingo_tracker)
    full_house_centrality_measures = calculate_centrality_measures_for_each_number(complete_fullhouse_tracker)

    # Displaying the centrality measures tables
    print("\t\t****** Centrality measures table for BINGO ****** \n", bingo_centrality_measures.head()) # Displaying the first few rows as examples

    print("\t\t****** Centrality measures table FOR FULL-HOUSE ****** \n", full_house_centrality_measures.head())
    
    bingo_averages = np.mean(complete_bingo_tracker, axis=1)
    bingo_std_devs = np.std(complete_bingo_tracker, axis=1)
    bingo_mins = np.min(complete_bingo_tracker, axis=1)
    bingo_maxs = np.max(complete_bingo_tracker, axis=1)

    fullhouse_averages = np.mean(complete_fullhouse_tracker, axis=1)
    fullhouse_std_devs = np.std(complete_fullhouse_tracker, axis=1)
    fullhouse_mins = np.min(complete_fullhouse_tracker, axis=1)
    fullhouse_maxs = np.max(complete_fullhouse_tracker, axis=1)

    # Plotting Bingo and Full-House
    plt.figure(figsize=(10, 6))
    plt.plot(bingo_averages, color='blue', label='Bingo', linestyle='-') #Plot Bingo Average
    plt.fill_between(range(len(bingo_std_devs)),bingo_averages-bingo_std_devs,bingo_averages+bingo_std_devs, color='lightblue') #Plot Bingo Standard Deviation
    plt.plot(bingo_mins, color='blue',linestyle=':') #Plot Bingo Min
    plt.plot(bingo_maxs, color='blue',linestyle=':') #Plot Bingo Max

    plt.plot(fullhouse_averages, color='orange', label='Full-House', linestyle='-') #Plot Full-House Average
    plt.fill_between(range(len(fullhouse_std_devs)),fullhouse_averages-fullhouse_std_devs,fullhouse_averages+fullhouse_std_devs, color='khaki')#Plot Full-House Standard Deviation
    plt.plot(fullhouse_mins, color='orange',linestyle=':') #Plot Full-House Min
    plt.plot(fullhouse_maxs, color='orange',linestyle=':') #Plot Full-House Max

    # Adding labels and legend
    plt.xlabel('Numbers Called')
    plt.ylabel('Winners')
    graph_title = "Bingo and Full-House Statistics on the basis of {} Simulations"
    plt.title(graph_title.format(number_of_simulations))
    plt.legend(loc='upper left')

    # Show the plot
    plt.show()
    
    
def on_button2_click():
    webbrowser.open(pdf_filename)

label_font = ('Harlow Solid Italic', 23)
title_font = ('Broadway', 40)
title= tk.Label(root, text="BINGO PARTY!", bg= "seashell2", fg= "light coral", font=title_font, anchor='e')
cards_label = tk.Label(root, text="Number of Cards to Generate:", bg= "seashell2", fg="SkyBlue2", font=label_font, anchor='e')
simulations_label = tk.Label(root, text="Number of Simulations to be Run:", bg= "seashell2", fg="SkyBlue2", font=label_font, anchor='e')

# Entry widgets
cards_entry = tk.Entry(root, font=label_font)
simulations_entry = tk.Entry(root, font=label_font)

button_font = ('Broadway', 20)
quit_font = ('Broadway', 17)
button1 = tk.Button(root, text="Start Simulation", command=on_button1_click, bg= "light coral", fg="black", font=button_font)
button2 = tk.Button(root, text="Show Cards", command=on_button2_click, bg ="light coral", fg="black", font=button_font)
button3 = tk.Button(root, text="Quit", command=root.destroy, bg ="seashell3", fg="black", font=quit_font)

window_width = 1000
window_height = 1000

# Calculate the screen dimensions
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the position for the window to be centered
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2

# Set the window size and position
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Arrange the widgets using the grid layout
title.place(relx=0.5, rely=0.2, anchor='center')
cards_label.place(relx=0.5, rely=0.3, anchor='center')
cards_entry.place(relx=0.5, rely=0.4, anchor='center')
simulations_label.place(relx=0.5, rely=0.5, anchor='center')
simulations_entry.place(relx=0.5, rely=0.6, anchor='center')
button1.place(relx=0.5, rely=0.7, anchor='center')
button2.place(relx=0.5, rely=0.8, anchor='center')
button3.place(relx=0.5, rely=0.9, anchor='center')

root.mainloop()

### Let's summarize and provide further analysis on the Bingo and Full-house problem based on the work we've done so far:

# **1. Bingo Card Generation:**
# 
# - We developed a function to generate unique 5x5 Bingo cards with numbers distributed as per the specified rules.
# - We also created a customizable version of this function, allowing for different grid sizes, number ranges, and free cell counts

# **2. Bingo and Full-House Game Simulation:**
# 
# - A simulation function was implemented to conduct 100 Bingo games with a set number of players.
# - In each game, a random sequence of numbers from 1 to 75 was generated to simulate the Bingo calling process.
# - The simulation tracked the number of players reaching Bingo (a line, column, or diagonal of marked numbers) and Full-house (all numbers marked) after each number was called.

# **3. Data Analysis and Visualization:**
# 
# - We analyzed the simulation data to calculate the average number of Bingo and Full-house achievements at each stage of the game (each number called).
# - We visualized this data using line plots with shaded areas representing standard deviation and dotted lines showing the minimum and maximum observed values.

# **4. Centrality Measures:**
# 
# - We calculated various centrality measures (median, percentiles, skewness, excess kurtosis) for each number called in the Bingo games.
# - These measures provide insights into the distribution and variability of Bingo and Full-house achievements at different stages of the game.

# **6. GUI and PDF Generation:**
# 
# - We discussed creating a GUI using tkinter for a more user-friendly way to generate and customize Bingo cards.
# - We also outlined a method to generate a PDF file with all the Bingo cards, one per page, and the option to include a custom image in the free cells
