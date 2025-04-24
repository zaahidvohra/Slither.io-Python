import customtkinter as ctk
import subprocess
import sys
import os
from PIL import Image, ImageTk
from src.services.dbhelper import DatabaseService
import pygame  # Add this import for music functionality

class MainMenu:
    def __init__(self):
        # Set theme and appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Initialize pygame for music
        pygame.init()
        pygame.mixer.init()
        self.music_playing = False
        self.menu_music_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "Sound", "menu_bgm.mp3")
        
        # Create root window
        self.root = ctk.CTk()
        self.root.title("Slither.io Clone")
        self.root.geometry("600x920")
        self.root.resizable(False, False)
        
        # Initialize variables
        self.game_mode = ctk.StringVar(value="single_player")
        self.player1_name = ctk.StringVar(value="Player_1")
        self.player2_name = ctk.StringVar(value="Player_2")
        self.sound_effects = ctk.BooleanVar(value=True)
        self.music = ctk.BooleanVar(value=True)
        
        # Initialize database service
        self.db_service = DatabaseService()
        
        # Create UI elements
        self.create_welcome_header()
        self.create_game_mode_section()
        self.create_player_name_section()
        self.create_sound_controls()
        self.create_leaderboard()
        self.create_buttons()
        
        # Update player name fields based on initial game mode
        self.update_player_fields()
        
        # Load leaderboard data from database
        self.load_leaderboard_data()
        
        # Start playing music when menu loads
        self.start_menu_music()
        
        # Set up a protocol for when the window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.exit_program)
        
    def create_welcome_header(self):
        # Logo/Welcome section (you can replace with your own logo image)
        self.header_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Try to load a logo image (you would need to create this file)
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_logo.png")
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((80, 80))
            self.logo = ImageTk.PhotoImage(logo_img)
            self.logo_label = ctk.CTkLabel(self.header_frame, image=self.logo, text="")
            self.logo_label.pack(side="left", padx=15, pady=15)
        except:
            # If logo can't be loaded, use text instead
            pass
        
        # Welcome message
        title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=10, pady=15, fill="both", expand=True)
        
        welcome_label = ctk.CTkLabel(
            title_frame, 
            text="Welcome to Slither.io Clone!", 
            font=ctk.CTkFont(family="Arial", size=24, weight="bold")
        )
        welcome_label.pack(anchor="w", pady=(0, 5))
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Slither your way to the top of the leaderboard!",
            font=ctk.CTkFont(family="Arial", size=14)
        )
        subtitle_label.pack(anchor="w")
    
    def create_game_mode_section(self):
        # Game mode selection
        mode_frame = ctk.CTkFrame(self.root, corner_radius=10)
        mode_frame.pack(fill="x", padx=20, pady=10)
        
        mode_label = ctk.CTkLabel(
            mode_frame,
            text="Select Game Mode",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold")
        )
        mode_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Radio buttons for game mode
        single_radio = ctk.CTkRadioButton(
            mode_frame,
            text="Single Player",
            variable=self.game_mode,
            value="single_player",
            command=self.on_game_mode_changed,
            font=ctk.CTkFont(size=14)
        )
        single_radio.pack(anchor="w", padx=25, pady=5)
    
        multi_radio = ctk.CTkRadioButton(
            mode_frame,
            text="Two Player",
            variable=self.game_mode,
            value="two_player",
            command=self.on_game_mode_changed,
            font=ctk.CTkFont(size=14)
        )
        multi_radio.pack(anchor="w", padx=25, pady=(5, 15))
    
    def on_game_mode_changed(self):
        """Handle game mode change"""
        self.update_player_fields()
        self.update_leaderboard_ui()

    def create_player_name_section(self):
        # Player name input section
        self.player_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.player_frame.pack(fill="x", padx=20, pady=10)
        
        name_label = ctk.CTkLabel(
            self.player_frame,
            text="Player Names",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold")
        )
        name_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Player 1 name input
        self.p1_frame = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        self.p1_frame.pack(fill="x", padx=15, pady=5)
        
        p1_label = ctk.CTkLabel(self.p1_frame, text="Player 1:", font=ctk.CTkFont(size=14))
        p1_label.pack(side="left", padx=(10, 5))
        
        p1_entry = ctk.CTkEntry(self.p1_frame, textvariable=self.player1_name, width=200)
        p1_entry.pack(side="left", padx=5)
        
        # Player 2 name input (will be shown/hidden based on game mode)
        self.p2_frame = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        self.p2_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        p2_label = ctk.CTkLabel(self.p2_frame, text="Player_2:", font=ctk.CTkFont(size=14))
        p2_label.pack(side="left", padx=(10, 5))
        
        p2_entry = ctk.CTkEntry(self.p2_frame, textvariable=self.player2_name, width=200)
        p2_entry.pack(side="left", padx=5)
    
    def create_sound_controls(self):
        # Sound controls section
        sound_frame = ctk.CTkFrame(self.root, corner_radius=10)
        sound_frame.pack(fill="x", padx=20, pady=10)
        
        sound_label = ctk.CTkLabel(
            sound_frame,
            text="Sound Settings",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold")
        )
        sound_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Sound effects switch
        effects_switch = ctk.CTkSwitch(
            sound_frame,
            text="Sound Effects",
            variable=self.sound_effects,
            font=ctk.CTkFont(size=14)
        )
        effects_switch.pack(anchor="w", padx=25, pady=5)
        
        # Music switch
        music_switch = ctk.CTkSwitch(
            sound_frame,
            text="Background Music",
            variable=self.music,
            command=self.toggle_music_from_switch,
            font=ctk.CTkFont(size=14)
        )
        music_switch.pack(anchor="w", padx=25, pady=(5, 15))
    
    def create_leaderboard(self):
        # Leaderboard section
        self.lb_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.lb_frame.pack(fill="x", padx=20, pady=10)
        
        self.lb_label = ctk.CTkLabel(
            self.lb_frame,
            text="Leaderboard",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold")
        )
        self.lb_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Leaderboard will be populated by load_leaderboard_data method
        self.lb_frame.pack(pady=(10, 15))
    
    def create_buttons(self):
        # Action buttons
        button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Exit button
        exit_button = ctk.CTkButton(
            button_frame,
            text="Exit",
            command=self.exit_program,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            width=100
        )
        exit_button.pack(side="left", padx=20)

        # Mute Button
        self.mute_button = ctk.CTkButton(
            button_frame,
            text="Mute Music",
            command=self.toggle_menu_music,
            fg_color="#A9A9A9",
            hover_color="#2c2c2c",
            width=100
        )
        self.mute_button.pack(side="left", padx=20)
        
        # Play button
        play_button = ctk.CTkButton(
            button_frame,
            text="Play Game",
            command=self.start_game,
            fg_color="#2ECC71",
            hover_color="#27AE60",
            font=ctk.CTkFont(weight="bold"),
            width=150
        )
        play_button.pack(side="right", padx=20)
    
    def update_player_fields(self):
        # Show/hide player 2 input based on game mode
        if self.game_mode.get() == "single_player":
            self.p2_frame.pack_forget()
        else:
            self.p2_frame.pack(fill="x", padx=15, pady=(5, 15))
    
    def load_leaderboard_data(self):
        """Load leaderboard data from database"""
        # Fetch top 5 players (default is single player mode)
        self.leaderboard_data = self.db_service.fetch_leaderboard()
        
        # Update UI with the data
        self.update_leaderboard_ui()
    
    def update_leaderboard_ui(self):
        """Update leaderboard UI elements with current data"""
        # Clear existing elements (except the title label)
        for widget in self.lb_frame.winfo_children():
            if widget != self.lb_label:  # Keep the title
                widget.destroy()
        
        mode = "multi" if self.game_mode.get() == "two_player" else "single"
        self.leaderboard_data = self.db_service.fetch_leaderboard(mode)
        # Recreate header row
        header_frame = ctk.CTkFrame(self.lb_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(0, 5))
    
        rank_header = ctk.CTkLabel(header_frame, text="Rank", width=40, font=ctk.CTkFont(weight="bold"))
        rank_header.pack(side="left", padx=5)
    
        name_header = ctk.CTkLabel(header_frame, text="Name", width=120, font=ctk.CTkFont(weight="bold"))
        name_header.pack(side="left", padx=5)
    
        # Add Wins column for multiplayer mode
        if mode == "multi":
            wins_header = ctk.CTkLabel(header_frame, text="Wins", width=40, font=ctk.CTkFont(weight="bold"))
            wins_header.pack(side="left", padx=5)
    
        score_header = ctk.CTkLabel(header_frame, text="Score", width=60, font=ctk.CTkFont(weight="bold"))
        score_header.pack(side="left", padx=5)
        
        # Fill with leaderboard data
        for i, entry in enumerate(self.leaderboard_data, 1):
            entry_frame = ctk.CTkFrame(self.lb_frame, fg_color="transparent")
            entry_frame.pack(fill="x", padx=15, pady=2)
        
            rank_label = ctk.CTkLabel(entry_frame, text=f"{i}", width=40)
            rank_label.pack(side="left", padx=5)
        
            name_label = ctk.CTkLabel(entry_frame, text=entry[0], width=120, anchor="w")
            name_label.pack(side="left", padx=5)
        
            if mode == "multi":
                # Format: (name, score, wins)
                wins_label = ctk.CTkLabel(entry_frame, text=str(entry[2]), width=40)
                wins_label.pack(side="left", padx=5)
                score_label = ctk.CTkLabel(entry_frame, text=str(entry[1]), width=60)
            else:
                # Format: (name, score)
                score_label = ctk.CTkLabel(entry_frame, text=str(entry[1]), width=60)
        
            score_label.pack(side="left", padx=5)
    
    def exit_program(self):
        # Stop music before exiting
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.quit()
        
        self.root.destroy()
        os._exit(0)
    
    def start_menu_music(self):
        """Start playing menu background music"""
        try:
            pygame.mixer.music.load(self.menu_music_path)
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            self.music_playing = True
            self.mute_button.configure(text="Mute Music")
        except Exception as e:
            print(f"Error playing music: {e}")
    
    def toggle_menu_music(self):
        """Toggle menu music on/off"""
        if self.music_playing:
            pygame.mixer.music.pause()
            self.music_playing = False
            self.mute_button.configure(text="Unmute Music")
        else:
            pygame.mixer.music.unpause()
            self.music_playing = True
            self.mute_button.configure(text="Mute Music")
    
    def toggle_music_from_switch(self):
        """Handle music toggle from the switch in sound settings"""
        if self.music.get():  # If music should be on
            if not self.music_playing:
                pygame.mixer.music.unpause()
                self.music_playing = True
                self.mute_button.configure(text="Mute Music")
        else:  # If music should be off
            if self.music_playing:
                pygame.mixer.music.pause()
                self.music_playing = False
                self.mute_button.configure(text="Unmute Music")
    
    def start_game(self):
        # Get player names
        p1_name = self.player1_name.get()
        p2_name = self.player2_name.get()
        
        # Check if names are provided
        if not p1_name:
            self.show_error("Please enter a name for Player 1")
            return
            
        if self.game_mode.get() == "two_player" and not p2_name:
            self.show_error("Please enter a name for Player 2")
            return
        
        # Validation checks
        if not p1_name or " " in p1_name:
            self.show_error("Player 1 name cannot be empty or contain spaces.")
            return
            
        if self.game_mode.get() == "two_player":
            if not p2_name or " " in p2_name:
                self.show_error("Player 2 name cannot be empty or contain spaces.")
                return
        
        # Check if username exists
        existing_users = []
        if self.game_mode.get() == "single_player":
            existing_users = self.db_service.check_username(p1_name)
        else:
            existing_users = self.db_service.check_username(p1_name, p2_name)
        
        if existing_users:
            # Show confirmation dialog for returning players
            self.confirm_returning_players(existing_users)
        else:
            # Register new players
            self.db_service.register_new_player(p1_name)
            if self.game_mode.get() == "two_player":
                self.db_service.register_new_player(p2_name)
            self.launch_game()
    
    def confirm_returning_players(self, existing_users):
        """Show dialog to confirm if the user is the same person as a returning player"""
        # Create confirmation dialog
        confirm_window = ctk.CTkToplevel(self.root)
        confirm_window.title("Returning Player")
        confirm_window.geometry("400x200")
        confirm_window.resizable(False, False)
        
        message = f"Player{'s' if len(existing_users) > 1 else ''} {', '.join(existing_users)} already exist{'s' if len(existing_users) == 1 else ''}.\n\nIf you are returning, click Continue. Otherwise, change your name."
        
        confirm_label = ctk.CTkLabel(
            confirm_window,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=350
        )
        confirm_label.pack(pady=(30, 20))
        
        button_frame = ctk.CTkFrame(confirm_window, fg_color="transparent")
        button_frame.pack(pady=10)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=confirm_window.destroy,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            width=100
        )
        cancel_button.pack(side="left", padx=10)
        
        continue_button = ctk.CTkButton(
            button_frame,
            text="Continue",
            command=lambda: [confirm_window.destroy(), self.launch_game()],
            fg_color="#2ECC71",
            hover_color="#27AE60",
            width=100
        )
        continue_button.pack(side="left", padx=10)
        
        # Make the window modal
        confirm_window.transient(self.root)
        confirm_window.grab_set()
    
    def launch_game(self):
        """Launch the game process"""
        # Get game parameters
        mode = self.game_mode.get()
        p1_name = self.player1_name.get()
        p2_name = self.player2_name.get()
        sound = "on" if self.sound_effects.get() else "off"
        music = "on" if self.music.get() else "off"
        
        # Stop music before closing
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.quit()
        
        # Close the menu before launching the game
        self.root.destroy()
        
        # Use Python executable to start the game (modify path as needed)
        main_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'main.py')
        python_executable = sys.executable
        
        # Pass all parameters to the game
        subprocess.Popen([
            python_executable, 
            main_py_path, 
            mode, 
            p1_name, 
            p2_name if mode == "two_player" else "", 
            sound, 
            music
        ])
    
    def show_error(self, message):
        error_window = ctk.CTkToplevel(self.root)
        error_window.title("Error")
        error_window.geometry("350x150")
        error_window.resizable(False, False)
        
        error_label = ctk.CTkLabel(
            error_window,
            text=message,
            font=ctk.CTkFont(size=14)
        )
        error_label.pack(pady=(30, 20))
        
        ok_button = ctk.CTkButton(
            error_window,
            text="OK",
            command=error_window.destroy,
            width=100
        )
        ok_button.pack(pady=10)
        
        # Make the error window modal
        error_window.transient(self.root)
        error_window.grab_set()
        self.root.wait_window(error_window)

def run_menu():
    app = MainMenu()
    app.root.mainloop()

if __name__ == "__main__":
    run_menu()