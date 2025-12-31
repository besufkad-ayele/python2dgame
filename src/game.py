"""
Ball Catch Game - Modern Arcade Game
A complete 2D ball catching game with modern UI/UX
"""

from graphics import *
import time
import random
import math
import os
try:
    import winsound
except ImportError:  # pragma: no cover
    winsound = None
from enum import Enum

class GameState(Enum):
    LOADING = 1
    MENU = 2
    PLAYING = 3
    PAUSED = 4
    GAME_OVER = 5
    INSTRUCTIONS = 6
    SETTINGS = 7
    CUSTOMIZE = 8

class GameSettings:
    def __init__(self):
        self.sound_enabled = True
        self.music_enabled = True
        self.skin_color = "#3b2416"
        self.hair_color = "black"
        self.shirt_color = "#2563eb"
        self.pants_color = "#111827"
        self.difficulty = "normal"


class PlayerSprite:
    def __init__(self, window, center_x, foot_y, skin_color, hair_color, shirt_color, pants_color):
        self._window = window
        self._parts = []

        body_w = 60
        body_h = 44
        head_r = 16
        leg_h = 32
        arm_w = 10
        arm_h = 34

        body_top_y = foot_y - (leg_h + body_h)
        body_bottom_y = body_top_y + body_h
        head_center_y = body_top_y - head_r - 6

        head = Circle(Point(center_x, head_center_y), head_r)
        head.setFill(skin_color)
        head.setOutline(skin_color)
        head.draw(window)

        hair = Circle(Point(center_x, head_center_y - 6), head_r)
        hair.setFill(hair_color)
        hair.setOutline(hair_color)
        hair.draw(window)

        face_cover = Circle(Point(center_x, head_center_y + 4), head_r)
        face_cover.setFill(skin_color)
        face_cover.setOutline(skin_color)
        face_cover.draw(window)

        shirt = Rectangle(
            Point(center_x - body_w / 2, body_top_y),
            Point(center_x + body_w / 2, body_bottom_y),
        )
        shirt.setFill(shirt_color)
        shirt.setOutline("white")
        shirt.setWidth(1)
        shirt.draw(window)

        left_arm = Rectangle(
            Point(center_x - body_w / 2 - arm_w, body_top_y + 4),
            Point(center_x - body_w / 2, body_top_y + 4 + arm_h),
        )
        left_arm.setFill(skin_color)
        left_arm.setOutline(skin_color)
        left_arm.draw(window)

        right_arm = Rectangle(
            Point(center_x + body_w / 2, body_top_y + 4),
            Point(center_x + body_w / 2 + arm_w, body_top_y + 4 + arm_h),
        )
        right_arm.setFill(skin_color)
        right_arm.setOutline(skin_color)
        right_arm.draw(window)

        pants = Rectangle(
            Point(center_x - body_w / 2 + 4, body_bottom_y),
            Point(center_x + body_w / 2 - 4, foot_y - 8),
        )
        pants.setFill(pants_color)
        pants.setOutline(pants_color)
        pants.draw(window)

        left_shoe = Rectangle(
            Point(center_x - body_w / 2 + 4, foot_y - 8),
            Point(center_x - 2, foot_y),
        )
        left_shoe.setFill("black")
        left_shoe.setOutline("black")
        left_shoe.draw(window)

        right_shoe = Rectangle(
            Point(center_x + 2, foot_y - 8),
            Point(center_x + body_w / 2 - 4, foot_y),
        )
        right_shoe.setFill("black")
        right_shoe.setOutline("black")
        right_shoe.draw(window)

        self._parts.extend([head, hair, face_cover, shirt, left_arm, right_arm, pants, left_shoe, right_shoe])
        self._p1 = Point(center_x - (body_w / 2 + arm_w), head_center_y - head_r)
        self._p2 = Point(center_x + (body_w / 2 + arm_w), foot_y)

    def move(self, dx, dy):
        for p in self._parts:
            p.move(dx, dy)
        self._p1 = Point(self._p1.getX() + dx, self._p1.getY() + dy)
        self._p2 = Point(self._p2.getX() + dx, self._p2.getY() + dy)

    def undraw(self):
        for p in self._parts:
            p.undraw()

    def getP1(self):
        return self._p1

    def getP2(self):
        return self._p2

class BallCatchGame:
    def __init__(self):
        self.settings = GameSettings()
        self.window = None
        self.state = GameState.LOADING
        self.width = 800
        self.height = 600
        
        # Game variables
        self.chances = 3
        self.level = 1
        self.speed = 2
        self.score = 0
        self.round_missed_in_level = False
        
        # Game objects
        self.player = None
        self.ball = None
        self.ground = None

        self._customize_preview = None
        
        # UI elements
        self.level_text = None
        self.chances_text = None
        self.score_text = None
        self.speed_text = None
        
        # Animation variables
        self.animation_counter = 0
        self.fade_alpha = 0

        self._missed_this_level = False
        
    def create_window(self):
        """Create the game window"""
        self.window = GraphWin("Ball Catch Game", self.width, self.height)
        self.window.setBackground("black")

    def safe_get_key(self):
        """Read a key without crashing if the window is closed."""
        try:
            if self.window is None or self.window.isClosed():
                return None
            return self.window.getKey()
        except Exception:
            return None

    def clear_screen(self):
        """Remove all drawn objects from the window."""
        if not self.window:
            return
        for item in self.window.items[:]:
            item.undraw()
        
    def play_sound(self, sound_name):
        """Play sound effects using Windows system audio (no external files)."""
        if not self.settings.sound_enabled:
            return
        if winsound is None:
            return

        if sound_name == "hit":
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        elif sound_name == "miss":
            winsound.MessageBeep(winsound.MB_ICONHAND)
        elif sound_name == "level_up":
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        elif sound_name == "menu":
            winsound.MessageBeep(winsound.MB_OK)
        elif sound_name == "game_over":
            winsound.MessageBeep(winsound.MB_ICONHAND)

    def play_music_cue(self, cue_name):
        """Play short music-like cues (beeps) if music is enabled."""
        if not self.settings.music_enabled:
            return
        if winsound is None:
            return

        if cue_name == "loading":
            for freq in (440, 554, 659):
                winsound.Beep(freq, 90)
        elif cue_name == "start":
            for freq in (523, 659, 784):
                winsound.Beep(freq, 80)
            
    def draw_loading_screen(self):
        """Draw loading screen with animation"""
        self.clear_screen()
        self.window.setBackground("black")

        self.play_music_cue("loading")
        
        # Create animated loading text
        loading_text = Text(Point(self.width//2, self.height//2), "BALL CATCH")
        loading_text.setSize(36)
        loading_text.setStyle("bold")
        loading_text.setTextColor("white")
        loading_text.draw(self.window)
        
        subtitle = Text(Point(self.width//2, self.height//2 + 50), "Loading...")
        subtitle.setSize(20)
        subtitle.setTextColor("gray")
        subtitle.draw(self.window)
        
        # Animate loading dots
        for i in range(3):
            time.sleep(0.5)
            subtitle.setText("Loading" + "." * (i + 1))
            self.window.update()
            
        time.sleep(1)
        loading_text.undraw()
        subtitle.undraw()
        
    def draw_main_menu(self):
        """Draw the main menu"""
        self.clear_screen()
        self.window.setBackground("darkblue")

        self.play_sound("menu")
        
        # Title
        title = Text(Point(self.width//2, 100), "BALL CATCH")
        title.setSize(36)
        title.setStyle("bold")
        title.setTextColor("white")
        title.draw(self.window)
        
        # Menu options
        options = [
            "1. Play Game",
            "2. Instructions",
            "3. Change Player",
            "4. Settings",
            "5. Exit"
        ]
        
        self.menu_texts = []
        for i, option in enumerate(options):
            text = Text(Point(self.width//2, 250 + i*60), option)
            text.setSize(24)
            text.setTextColor("white")
            text.draw(self.window)
            self.menu_texts.append(text)
            
        # Instructions at bottom
        info = Text(Point(self.width//2, self.height - 30), "Press number key to select option")
        info.setSize(14)
        info.setTextColor("gray")
        info.draw(self.window)
        
    def draw_instructions(self):
        """Draw instructions screen"""
        self.clear_screen()
        self.window.setBackground("darkgreen")
        
        title = Text(Point(self.width//2, 50), "HOW TO PLAY")
        title.setSize(36)
        title.setStyle("bold")
        title.setTextColor("white")
        title.draw(self.window)
        
        instructions = [
            "🎮 CONTROLS:",
            "• Use LEFT and RIGHT arrow keys to move",
            "• Press SPACE to pause during game",
            "• Press Q to quit to menu",
            "",
            "🎯 OBJECTIVE:",
            "• Catch the falling ball with your character",
            "• Each drop costs 1 chance (attempt)",
            "• Catching the ball clears the level",
            "",
            "� PROGRESSION:",
            "• On catch: Level +1 and Chances +3",
            "• Remaining chances carry over",
            "• Speed increases each level",
            "",
            "🏆 SCORING:",
            "• Points = Level × 10 per catch",
            "• Higher levels = more points",
            "",
            "Press ESC to return to main menu"
        ]
        
        for i, line in enumerate(instructions):
            text = Text(Point(self.width//2, 120 + i*25), line)
            text.setSize(16)
            if line.startswith("🎮") or line.startswith("🎯") or line.startswith("💡") or line.startswith("🏆"):
                text.setStyle("bold")
                text.setTextColor("yellow")
            else:
                text.setTextColor("white")
            text.draw(self.window)
            
    def draw_settings(self):
        """Draw settings screen"""
        self.clear_screen()
        self.window.setBackground("darkgray")
        
        title = Text(Point(self.width//2, 50), "SETTINGS")
        title.setSize(36)
        title.setStyle("bold")
        title.setTextColor("white")
        title.draw(self.window)
        
        settings_text = [
            f"1. Sound: {'ON' if self.settings.sound_enabled else 'OFF'}",
            f"2. Music: {'ON' if self.settings.music_enabled else 'OFF'}",
            f"3. Shirt Color: {self.settings.shirt_color}",
            f"4. Pants Color: {self.settings.pants_color}",
            f"5. Difficulty: {self.settings.difficulty.capitalize()}",
            "",
            "Press number to change",
            "Press ESC to return to menu"
        ]
        
        for i, line in enumerate(settings_text):
            text = Text(Point(self.width//2, 150 + i*40), line)
            text.setSize(20)
            text.setTextColor("white")
            text.draw(self.window)
            
    def draw_customize_player(self):
        """Draw customize player screen."""
        self.clear_screen()
        self.window.setBackground("#1b1b1b")

        title = Text(Point(self.width//2, 60), "CHANGE PLAYER")
        title.setSize(36)
        title.setStyle("bold")
        title.setTextColor("white")
        title.draw(self.window)

        subtitle = Text(Point(self.width//2, 110), "Customize your outfit")
        subtitle.setSize(16)
        subtitle.setTextColor("gray")
        subtitle.draw(self.window)

        preview_label = Text(Point(self.width//2, 170), "Preview")
        preview_label.setSize(18)
        preview_label.setStyle("bold")
        preview_label.setTextColor("white")
        preview_label.draw(self.window)

        cx, foot_y = self.width // 2, 310
        self._customize_preview = PlayerSprite(
            self.window,
            cx,
            foot_y,
            self.settings.skin_color,
            self.settings.hair_color,
            self.settings.shirt_color,
            self.settings.pants_color,
        )

        items = [
            Text(Point(self.width//2, 400), f"1. Shirt Color: {self.settings.shirt_color}"),
            Text(Point(self.width//2, 450), f"2. Pants Color: {self.settings.pants_color}"),
            Text(Point(self.width//2, 500), "Press 1/2 to change, ESC to return"),
        ]
        items[0].setSize(22)
        items[1].setSize(22)
        items[2].setSize(14)
        items[0].setTextColor("white")
        items[1].setTextColor("white")
        items[2].setTextColor("gray")
        for it in items:
            it.draw(self.window)

    def initialize_game(self):
        """Initialize game objects"""
        self.clear_screen()
        self.window.setBackground("lightblue")

        self.chances = 3
        self.level = 1
        self.speed = 2
        self.score = 0
        self.round_missed_in_level = False
            
        # Draw ground
        self.ground = Rectangle(Point(0, self.height - 50), Point(self.width, self.height))
        self.ground.setFill("green")
        self.ground.draw(self.window)
        
        # Draw player (human sprite)
        self.player = PlayerSprite(
            self.window,
            self.width // 2,
            self.height - 50,
            self.settings.skin_color,
            self.settings.hair_color,
            self.settings.shirt_color,
            self.settings.pants_color,
        )
        
        # Initialize UI text
        self.level_text = Text(Point(50, 30), f"Level: {self.level}")
        self.level_text.setSize(16)
        self.level_text.setStyle("bold")
        self.level_text.setTextColor("white")
        self.level_text.draw(self.window)
        
        self.chances_text = Text(Point(200, 30), f"Chances: {self.chances}")
        self.chances_text.setSize(16)
        self.chances_text.setStyle("bold")
        self.chances_text.setTextColor("white")
        self.chances_text.draw(self.window)
        
        self.score_text = Text(Point(350, 30), f"Score: {self.score}")
        self.score_text.setSize(16)
        self.score_text.setStyle("bold")
        self.score_text.setTextColor("white")
        self.score_text.draw(self.window)
        
        self.speed_text = Text(Point(500, 30), f"Speed: {self.speed:.1f}")
        self.speed_text.setSize(16)
        self.speed_text.setStyle("bold")
        self.speed_text.setTextColor("white")
        self.speed_text.draw(self.window)

        self.update_ui()

    def update_ui(self):
        """Update UI text elements"""
        if self.level_text:
            self.level_text.setText(f"Level: {self.level}")
        if self.chances_text:
            self.chances_text.setText(f"Chances: {self.chances}")
        if self.score_text:
            self.score_text.setText(f"Score: {self.score}")
        if self.speed_text:
            self.speed_text.setText(f"Speed: {self.speed:.1f}")

    def create_new_ball(self):
        """Create a new falling ball"""
        x = random.randint(20, self.width - 20)
        self.ball = Circle(Point(x, 20), 10)
        self.ball.setFill("red")
        self.ball.draw(self.window)
        
    def check_collision(self):
        """Check if ball collides with player"""
        if not self.ball or not self.player:
            return False
            
        ball_center = self.ball.getCenter()
        player_p1 = self.player.getP1()
        player_p2 = self.player.getP2()
        
        # Check if ball is at player height and within player width
        if (ball_center.getY() >= player_p1.getY() - 10 and
            player_p1.getX() <= ball_center.getX() <= player_p2.getX()):
            return True
        return False
        
    def show_hit_effect(self):
        """Show visual effect when ball is caught"""
        effect = Text(Point(self.ball.getCenter().getX(), self.ball.getCenter().getY() - 20), "HIT!")
        effect.setSize(20)
        effect.setStyle("bold")
        effect.setTextColor("green")
        effect.draw(self.window)
        time.sleep(0.5)
        effect.undraw()

    def show_perfect_effect(self):
        effect = Text(Point(self.width // 2, 90), "PERFECT!")
        effect.setSize(26)
        effect.setStyle("bold")
        effect.setTextColor("#22c55e")
        effect.draw(self.window)
        time.sleep(0.8)
        effect.undraw()

    def pause_overlay(self):
        """Pause overlay that resumes without resetting game state."""
        self.state = GameState.PAUSED

        panel = Rectangle(Point(160, 210), Point(self.width - 160, 390))
        panel.setFill("#0f172a")
        panel.setOutline("#94a3b8")
        panel.setWidth(2)
        panel.draw(self.window)

        title = Text(Point(self.width // 2, 260), "PAUSED")
        title.setSize(32)
        title.setStyle("bold")
        title.setTextColor("white")
        title.draw(self.window)

        hint = Text(Point(self.width // 2, 320), "SPACE to resume | Q for menu")
        hint.setSize(16)
        hint.setTextColor("#cbd5e1")
        hint.draw(self.window)

        while True:
            key = self.safe_get_key()
            if key is None:
                self.state = GameState.MENU
                break
            if key == "space":
                self.state = GameState.PLAYING
                break
            if key == "q":
                self.state = GameState.MENU
                break

        title.undraw()
        hint.undraw()
        panel.undraw()
        
    def show_miss_effect(self):
        """Show visual effect when ball is missed"""
        effect = Text(Point(self.ball.getCenter().getX(), self.height - 25), "MISS!")
        effect.setSize(20)
        effect.setStyle("bold")
        effect.setTextColor("red")
        effect.draw(self.window)
        time.sleep(0.5)
        effect.undraw()
        
    def show_level_up(self):
        """Show level up animation"""
        level_up = Text(Point(self.width//2, self.height//2), f"LEVEL {self.level}!")
        level_up.setSize(36)
        level_up.setStyle("bold")
        level_up.setTextColor("yellow")
        level_up.draw(self.window)
        time.sleep(1)
        level_up.undraw()
        
    def show_game_over(self):
        """Show game over screen"""
        self.clear_screen()

        self.play_sound("game_over")

        self.window.setBackground("#120b0b")
        game_over = Text(Point(self.width//2, self.height//2 - 50), "GAME OVER")
        game_over.setSize(36)
        game_over.setStyle("bold")
        game_over.setTextColor("red")
        game_over.draw(self.window)
        
        final_score = Text(Point(self.width//2, self.height//2 + 20), f"Final Score: {self.score}")
        final_score.setSize(24)
        final_score.setTextColor("white")
        final_score.draw(self.window)
        
        restart = Text(Point(self.width//2, self.height//2 + 80), "Press SPACE to play again or ESC for menu")
        restart.setSize(16)
        restart.setTextColor("gray")
        restart.draw(self.window)
        
    def play_game(self):
        """Main game loop"""
        self.initialize_game()

        self.play_music_cue("start")
        
        # Show start message
        start_msg = Text(Point(self.width//2, self.height//2), "Press any key to start!")
        start_msg.setSize(24)
        start_msg.setTextColor("white")
        start_msg.draw(self.window)

        key = self.safe_get_key()
        if key is None:
            return
        start_msg.undraw()
        
        self._missed_this_level = False
        while self.chances > 0 and self.state == GameState.PLAYING:
            # Each ball drop consumes one chance (attempt)
            self.chances -= 1
            self.update_ui()
            if self.chances < 0:
                self.chances = 0

            self.create_new_ball()
            ball_falling = True
            hit = False
            missed = False
            
            while ball_falling and self.state == GameState.PLAYING:
                # Move ball
                self.ball.move(0, self.speed)
                
                # Handle input
                key = self.window.checkKey()
                if key == "Left" and self.player.getP1().getX() > 0:
                    self.player.move(-6, 0)
                elif key == "Right" and self.player.getP2().getX() < self.width:
                    self.player.move(6, 0)
                elif key == "q":
                    self.state = GameState.MENU
                    return
                elif key == "space":
                    self.pause_overlay()
                    if self.state != GameState.PLAYING:
                        return
                    
                # Check collision
                if self.check_collision():
                    hit = True
                    ball_falling = False
                    self.score += self.level * 10
                    self.play_sound("hit")
                    self.show_hit_effect()
                        
                # Check if ball reached bottom
                elif self.ball.getCenter().getY() > self.height - 50:
                    ball_falling = False
                    missed = True
                    self.play_sound("miss")
                    self.show_miss_effect()
                    
                self.update_ui()
                time.sleep(0.02)
                
            # Clean up ball
            if self.ball:
                self.ball.undraw()
                self.ball = None
                
            # Level resolution
            if hit:
                if not self._missed_this_level:
                    self.show_perfect_effect()

                self.level += 1
                self.chances += 3

                speed_step = 0.6
                if self.settings.difficulty == "easy":
                    speed_step = 0.4
                elif self.settings.difficulty == "hard":
                    speed_step = 0.85
                self.speed += speed_step

                self.play_sound("level_up")
                self.show_level_up()
                self._missed_this_level = False

            elif missed:
                self._missed_this_level = True
                if self.chances <= 0:
                    self.state = GameState.GAME_OVER
                    self.show_game_over()
                    return
                
        if self.chances <= 0:
            self.state = GameState.GAME_OVER
            self.show_game_over()
            
    def handle_menu_input(self, key):
        """Handle input in menu state"""
        if key == "1":
            self.state = GameState.PLAYING
        elif key == "2":
            self.state = GameState.INSTRUCTIONS
        elif key == "3":
            self.state = GameState.CUSTOMIZE
        elif key == "4":
            self.state = GameState.SETTINGS
        elif key == "5":
            self.window.close()
            return True
        return False
        
    def handle_settings_input(self, key):
        """Handle input in settings state"""
        if key == "1":
            self.settings.sound_enabled = not self.settings.sound_enabled
        elif key == "2":
            self.settings.music_enabled = not self.settings.music_enabled
        elif key == "3":
            colors = ["#2563eb", "#ef4444", "#22c55e", "#f59e0b", "#a855f7", "#06b6d4", "#ffffff"]
            current_index = colors.index(self.settings.shirt_color)
            self.settings.shirt_color = colors[(current_index + 1) % len(colors)]
        elif key == "4":
            colors = ["#111827", "#334155", "#7c2d12", "#1f2937", "#0f766e", "#000000"]
            current_index = colors.index(self.settings.pants_color)
            self.settings.pants_color = colors[(current_index + 1) % len(colors)]
        elif key == "5":
            difficulties = ["easy", "normal", "hard"]
            current_index = difficulties.index(self.settings.difficulty)
            self.settings.difficulty = difficulties[(current_index + 1) % len(difficulties)]

    def handle_customize_input(self, key):
        """Handle input in customize state"""
        if key == "1":
            colors = ["#2563eb", "#ef4444", "#22c55e", "#f59e0b", "#a855f7", "#06b6d4", "#ffffff"]
            current_index = colors.index(self.settings.shirt_color)
            self.settings.shirt_color = colors[(current_index + 1) % len(colors)]
        elif key == "2":
            colors = ["#111827", "#334155", "#7c2d12", "#1f2937", "#0f766e", "#000000"]
            current_index = colors.index(self.settings.pants_color)
            self.settings.pants_color = colors[(current_index + 1) % len(colors)]
            
    def run(self):
        """Main game loop"""
        self.create_window()
        self.draw_loading_screen()
        self.state = GameState.MENU
        
        running = True
        while running:
            if self.window is None or self.window.isClosed():
                break
            if self.state == GameState.MENU:
                self.draw_main_menu()
                key = self.safe_get_key()
                if key is None:
                    break
                if self.handle_menu_input(key):
                    break
                    
            elif self.state == GameState.INSTRUCTIONS:
                self.draw_instructions()
                key = self.safe_get_key()
                if key is None:
                    break
                if key == "Escape":
                    self.state = GameState.MENU
                    
            elif self.state == GameState.SETTINGS:
                self.draw_settings()
                key = self.safe_get_key()
                if key is None:
                    break
                if key == "Escape":
                    self.state = GameState.MENU
                else:
                    self.handle_settings_input(key)

            elif self.state == GameState.CUSTOMIZE:
                self.draw_customize_player()
                key = self.safe_get_key()
                if key is None:
                    break
                if key == "Escape":
                    if self._customize_preview is not None:
                        self._customize_preview.undraw()
                        self._customize_preview = None
                    self.state = GameState.MENU
                else:
                    self.handle_customize_input(key)
                    if self._customize_preview is not None:
                        self._customize_preview.undraw()
                        self._customize_preview = None
                    # Redraw screen to reflect updated colors
                    continue
                    
            elif self.state == GameState.PLAYING:
                self.play_game()
                
            elif self.state == GameState.GAME_OVER:
                key = self.safe_get_key()
                if key is None:
                    break
                if key == "space":
                    self.state = GameState.PLAYING
                elif key == "Escape":
                    self.state = GameState.MENU
                    
            elif self.state == GameState.PAUSED:
                self.clear_screen()
                self.window.setBackground("#0f172a")
                pause_text = Text(Point(self.width//2, self.height//2), "PAUSED")
                pause_text.setSize(36)
                pause_text.setStyle("bold")
                pause_text.setTextColor("white")
                pause_text.draw(self.window)

                hint = Text(Point(self.width//2, self.height//2 + 60), "SPACE to resume | Q for menu")
                hint.setSize(16)
                hint.setTextColor("gray")
                hint.draw(self.window)
                
                key = self.safe_get_key()
                if key is None:
                    break
                if key == "space":
                    self.state = GameState.PLAYING
                elif key == "q":
                    self.state = GameState.MENU
                    
                pause_text.undraw()
                hint.undraw()
                
        if self.window:
            self.window.close()

if __name__ == "__main__":
    game = BallCatchGame()
    game.run()
