#!/usr/bin/env python3
"""QwertyMaster - Native Desktop Qwerty Typing Trainer"""

import tkinter as tk
from tkinter import font as tkfont
import random
import time
import json
import urllib.request
import threading
import os

# ─── Colors (dark theme) ───────────────────────────────────────────────
BG = "#0f172a"
SECONDARY_BG = "#1e293b"
BORDER = "#334155"
TEXT = "#e2e8f0"
MUTED = "#94a3b8"
DIM = "#64748b"
ACCENT = "#10b981"
ACCENT_HOVER = "#059669"
ERROR = "#ef4444"
ERROR_BG = "#2d1515"
KEY_BG = "#334155"
KEY_TEXT = "#cbd5e1"
WHITE = "#ffffff"
BRIGHT_TEXT = "#f1f5f9"

# ─── Qwerty Layout ─────────────────────────────────────────────────────
QWERTY_LAYOUT = [
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='],
    ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
    ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'Enter'],
    ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
    ['Space']
]

SHIFT_MAP = {
    '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7',
    '*': '8', '(': '9', ')': '0', '{': '[', '}': ']', '"': "'", '<': ',',
    '>': '.', '?': '/', '+': '=', '_': '-', ':': ';', '|': '\\', '~': '`'
}

# Build char -> (row, col) map
CHAR_TO_POS = {}
for r_idx, row in enumerate(QWERTY_LAYOUT):
    for c_idx, key in enumerate(row):
        CHAR_TO_POS[key] = (r_idx, c_idx)
        if len(key) == 1 and key.isalpha():
            CHAR_TO_POS[key.upper()] = (r_idx, c_idx)
for shifted, original in SHIFT_MAP.items():
    if original in CHAR_TO_POS:
        CHAR_TO_POS[shifted] = CHAR_TO_POS[original]

# ─── Stories ────────────────────────────────────────────────────────────
STORIES = [
    "Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do: once or twice she had peeped into the book her sister was reading, but it had no pictures or conversations in it, 'and what is the use of a book,' thought Alice 'without pictures or conversation?' So she was considering in her own mind (as well as she could, for the hot day made her feel very sleepy and stupid), whether the pleasure of making a daisy-chain would be worth the trouble of getting up and picking the daisies, when suddenly a White Rabbit with pink eyes ran close by her.",
    "You will rejoice to hear that no disaster has accompanied the commencement of an enterprise which you have regarded with such evil forebodings. I arrived here yesterday, and my first task is to assure my dear sister of my welfare and increasing confidence in the success of my undertaking. I am already far north of London, and as I walk in the streets of Petersburgh, I feel a cold northern breeze play upon my cheeks, which braces my nerves and fills me with delight. Do you understand this feeling? This breeze, which has travelled from the regions towards which I am advancing, gives me a foretaste of those icy climes.",
    "To Sherlock Holmes she is always the woman. I have seldom heard him mention her under any other name. In his eyes she eclipses and predominates the whole of her sex. It was not that he felt any emotion akin to love for Irene Adler. All emotions, and that one particularly, were abhorrent to his cold, precise but admirably balanced mind. He was, I take it, the most perfect reasoning and observing machine that the world has seen, but as a lover he would have placed himself in a false position. He never spoke of the softer passions, save with a gibe and a sneer.",
    "In my younger and more vulnerable years my father gave me some advice that I've been turning over in my mind ever since. 'Whenever you feel like criticizing any one,' he told me, 'just remember that all the people in this world haven't had the advantages that you've had.' He didn't say any more, but we've always been unusually communicative in a reserved way, and I understood that he meant a great deal more than that.",
    "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife. However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters.",
    "Call me Ishmael. Some years ago, having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world. It is a way I have of driving off the spleen and regulating the circulation. Whenever I find myself growing grim about the mouth; whenever it is a damp, drizzly November in my soul; whenever I find myself involuntarily pausing before coffin warehouses, and bringing up the rear of every funeral I meet, I account it high time to get to sea as soon as I can.",
    "3 May. Bistritz. Left Munich at 8:35 P.M., on 1st May, arriving at Vienna early next morning; should have arrived at 6:46, but train was an hour late. Buda-Pesth seems a wonderful place, from the glimpse which I got of it from the train and the little I could walk through the streets. I feared to go very far from the station, as we had arrived late and would start as near the correct time as possible."
]


def fetch_gutenberg_text():
    """Try to fetch a random popular text from Project Gutenberg."""
    try:
        # Get popular books
        req = urllib.request.Request(
            'https://gutendex.com/books?languages=en&sort=popular',
            headers={'User-Agent': 'QwertyMaster/1.0'}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode('utf-8'))

        if not data.get('results'):
            return None

        # Pick one from top 15
        book = random.choice(data['results'][:15])
        text_url = book['formats'].get('text/plain; charset=utf-8') or book['formats'].get('text/plain')
        if not text_url:
            return None

        with urllib.request.urlopen(text_url, timeout=10) as resp:
            text = resp.read().decode('utf-8')

        # Clean Gutenberg markers
        markers = [
            "*** START OF THE PROJECT GUTENBERG EBOOK",
            "*** START OF THIS PROJECT GUTENBERG EBOOK",
            "***START OF THE PROJECT GUTENBERG EBOOK"
        ]
        start = -1
        for m in markers:
            start = text.find(m)
            if start != -1:
                nl = text.find('\n', start)
                start = nl + 1 if nl != -1 else start + 50
                break
        
        if start == -1: start = 1000 # Fallback skip header

        end_markers = [
            "*** END OF THE PROJECT GUTENBERG EBOOK",
            "*** END OF THIS PROJECT GUTENBERG EBOOK"
        ]
        end = -1
        for m in end_markers:
            end = text.find(m)
            if end != -1: break
        
        if end == -1: end = len(text) - 1000

        content = ' '.join(text[start:end].split())

        if len(content) > 1000:
            # Pick a better chunk (start after a full stop)
            s = random.randint(500, len(content) - 800)
            dot = content.find('. ', s)
            s = dot + 2 if dot != -1 else s
            
            # Find a good end point
            chunk = content[s:s + 600]
            last_dot = chunk.rfind('.')
            if last_dot != -1 and last_dot > 100:
                return chunk[:last_dot + 1].strip()
            return chunk.strip()

        return content
    except Exception as e:
        print(f"Gutenberg error: {e}")
        return None



# ─── QwertyMaster App ──────────────────────────────────────────────────────
class QwertyMasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QwertyMaster")
        self.root.configure(bg=BG)
        self.root.geometry("1050x780")
        self.root.minsize(900, 700)

        # Gamification Import
        try:
             import tkinter.messagebox
        except:
             pass

        # State
        self.current_text = ""
        self.typed = ""
        self.start_time = None
        self.errors = 0
        self.streak = 0
        self.max_streak = 0
        self.is_finished = False
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.key_widgets = {}  # (row, col) -> label widget

        # AI Competition State
        self.ai_mode = tk.StringVar(value="Solo")
        self.ai_progress = 0
        self.ai_wpm = 0
        self.ai_running = False
        self.ai_start_time = None
        self.difficulty = "Normal"
        self.ai_finished = False

        # Fonts
        self.font_title = tkfont.Font(family="Helvetica", size=28, weight="bold")
        self.font_subtitle = tkfont.Font(family="Helvetica", size=12)
        self.font_stat_label = tkfont.Font(family="Helvetica", size=10)
        self.font_stat_value = tkfont.Font(family="Helvetica", size=20, weight="bold")
        self.font_mono = tkfont.Font(family="Courier", size=18)
        self.font_key = tkfont.Font(family="Helvetica", size=11, weight="bold")
        self.font_key_special = tkfont.Font(family="Helvetica", size=9, weight="bold")
        self.font_btn = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.font_modal_title = tkfont.Font(family="Helvetica", size=22, weight="bold")
        self.font_modal_label = tkfont.Font(family="Helvetica", size=10)
        self.font_modal_value = tkfont.Font(family="Helvetica", size=22, weight="bold")
        self.font_footer = tkfont.Font(family="Helvetica", size=10)
        self.font_combo = tkfont.Font(family="Helvetica", size=16, weight="bold", slant="italic")

        self.music_manager = None

        self._build_ui()
        self.root.bind("<Key>", self._on_key)
        self.root.focus_force()

        # Check Layout
        self._check_layout()

        self.load_game()

    def _check_layout(self):
        try:
            import subprocess
            result = subprocess.run(['setxkbmap', '-print'], capture_output=True, text=True)
            if 'us' not in result.stdout.lower():
                 tk.messagebox.showwarning("Layout Warning", "English US layout not detected!\nPlease switch your keyboard input method to English (US) for the best experience.")
        except Exception as e:
            print(f"Error checking layout: {e}")


    def _build_ui(self):
        # ── Header ──
        header = tk.Frame(self.root, bg=BG)
        header.pack(pady=(20, 5))
        tk.Label(header, text="QwertyMaster", font=self.font_title,
                 fg=ACCENT, bg=BG).pack()
        
        # Difficulty Selector
        diff_frame = tk.Frame(header, bg=BG)
        diff_frame.pack(pady=5)
        tk.Label(diff_frame, text="AI Competition:", font=self.font_subtitle, fg=MUTED, bg=BG).pack(side="left")
        
        for d in ["Solo", "Easy", "Normal", "Hard"]:
            btn = tk.Radiobutton(diff_frame, text=d, variable=self.ai_mode, value=d,
                                 command=self._on_ai_change, font=("Helvetica", 10),
                                 bg=BG, fg=TEXT, selectcolor=SECONDARY_BG, 
                                 activebackground=BG, activeforeground=ACCENT)
            btn.pack(side="left", padx=5)
        
        tk.Label(header, text="Master the Qwerty layout with Project Gutenberg stories",
                 font=self.font_subtitle, fg=MUTED, bg=BG).pack()

        # ── Status ──
        status_frame = tk.Frame(header, bg=BG)
        status_frame.pack(pady=(10, 0))


        # ── Stats Bar ──
        stats_frame = tk.Frame(self.root, bg=BG)
        stats_frame.pack(pady=(15, 10), padx=30, fill="x")

        self.wpm_var = tk.StringVar(value="0")
        self.acc_var = tk.StringVar(value="100%")
        self.streak_var = tk.StringVar(value="0")
        self.score_var = tk.StringVar(value="0")
        self.combo_var = tk.StringVar(value="x0")

        for label_text, var in [("WPM", self.wpm_var), ("ACCURACY", self.acc_var), ("STREAK", self.streak_var), ("SCORE", self.score_var)]:
            card = tk.Frame(stats_frame, bg=SECONDARY_BG, highlightbackground=BORDER,
                            highlightthickness=1, padx=15, pady=10)
            card.pack(side="left", expand=True, fill="x", padx=5)
            tk.Label(card, text=label_text, font=self.font_stat_label,
                     fg=MUTED, bg=SECONDARY_BG).pack()
            tk.Label(card, textvariable=var, font=self.font_stat_value,
                     fg=TEXT, bg=SECONDARY_BG).pack()

        # Combo Overlay (Top Right of Window)
        self.combo_label = tk.Label(self.root, textvariable=self.combo_var, font=self.font_combo, fg=ACCENT, bg=BG)
        self.combo_label.place(relx=0.95, rely=0.05, anchor="ne")

        # AI Progress Bar
        self.ai_bar_frame = tk.Frame(self.root, bg=BG)
        self.ai_bar_frame.pack(fill="x", padx=30, pady=(0, 10))
        
        self.ai_label = tk.Label(self.ai_bar_frame, text="AI Progress:", font=("Helvetica", 9), fg=MUTED, bg=BG)
        self.ai_label.pack(side="left")
        
        self.ai_canvas = tk.Canvas(self.ai_bar_frame, height=10, bg=SECONDARY_BG, highlightthickness=0)
        self.ai_canvas.pack(side="left", fill="x", expand=True, padx=10)
        self.ai_rect = self.ai_canvas.create_rectangle(0, 0, 0, 10, fill=ERROR, width=0)

        # Player Progress Bar
        self.player_bar_frame = tk.Frame(self.root, bg=BG)
        self.player_bar_frame.pack(fill="x", padx=30, pady=(0, 10))
        
        self.player_label = tk.Label(self.player_bar_frame, text="Your Progress:", font=("Helvetica", 9), fg=MUTED, bg=BG)
        self.player_label.pack(side="left")
        
        self.player_canvas = tk.Canvas(self.player_bar_frame, height=10, bg=SECONDARY_BG, highlightthickness=0)
        self.player_canvas.pack(side="left", fill="x", expand=True, padx=10)
        self.player_rect = self.player_canvas.create_rectangle(0, 0, 0, 10, fill=ACCENT, width=0)


        # ── Typing Area ──
        typing_frame = tk.Frame(self.root, bg=SECONDARY_BG, highlightbackground=BORDER,
                                highlightthickness=1, padx=20, pady=20)
        typing_frame.pack(padx=30, fill="x")

        self.text_canvas = tk.Text(
            typing_frame, wrap="word", font=self.font_mono, bg=SECONDARY_BG,
            fg=DIM, height=7, borderwidth=0, highlightthickness=0,
            cursor="xterm", state="disabled", padx=5, pady=5
        )
        self.text_canvas.pack(fill="x")

        # Tag configuration for character styling
        self.text_canvas.tag_configure("correct", foreground=ACCENT)
        self.text_canvas.tag_configure("incorrect", foreground=ERROR, background=ERROR_BG)
        self.text_canvas.tag_configure("current", foreground=BRIGHT_TEXT)
        self.text_canvas.tag_configure("pending", foreground=DIM)

        # ── Keyboard ──
        kb_outer = tk.Frame(self.root, bg=SECONDARY_BG, highlightbackground=BORDER,
                            highlightthickness=1, padx=15, pady=15)
        kb_outer.pack(padx=30, pady=(15, 5), fill="x")
        self._build_keyboard(kb_outer)

        # ── Footer ──
        tk.Label(self.root, text="Tip: Focus on accuracy first, speed will follow.",
                 font=self.font_footer, fg=MUTED, bg=BG).pack(pady=(10, 5))

        # ── Modal Overlay (hidden by default) ──
        self.modal_overlay = tk.Frame(self.root, bg="")
        self.modal_frame = None

    def _build_keyboard(self, parent):
        for r_idx, row in enumerate(QWERTY_LAYOUT):
            row_frame = tk.Frame(parent, bg=SECONDARY_BG)
            row_frame.pack(pady=2)

            for c_idx, key in enumerate(row):
                is_special = len(key) > 1
                is_space = key == "Space"
                display = "" if is_space else key

                width = 18 if is_space else (6 if is_special else 3)
                f = self.font_key_special if is_special else self.font_key

                lbl = tk.Label(
                    row_frame, text=display, font=f,
                    bg=KEY_BG, fg=KEY_TEXT, width=width, height=2,
                    relief="flat", padx=2, pady=0
                )
                lbl.pack(side="left", padx=2)
                self.key_widgets[(r_idx, c_idx)] = lbl

    def _highlight_key(self, char):
        """Highlight the key for the given character."""
        # Reset all keys
        for lbl in self.key_widgets.values():
            lbl.configure(bg=KEY_BG, fg=KEY_TEXT)

        if not char:
            return

        pos = CHAR_TO_POS.get(char)
        if pos and pos in self.key_widgets:
            self.key_widgets[pos].configure(bg=ACCENT, fg=WHITE)
        elif char == ' ':
            # Space bar is always (4, 0)
            space_pos = (4, 0)
            if space_pos in self.key_widgets:
                self.key_widgets[space_pos].configure(bg=ACCENT, fg=WHITE)

    def _render_text(self):
        """Render the text with correct/incorrect/current styling."""
        self.text_canvas.configure(state="normal")
        self.text_canvas.delete("1.0", "end")

        for i, char in enumerate(self.current_text):
            if i < len(self.typed):
                if self.typed[i] == char:
                    tag = "correct"
                else:
                    tag = "incorrect"
            elif i == len(self.typed):
                tag = "current"
            else:
                tag = "pending"
            self.text_canvas.insert("end", char, tag)

        # Auto-scroll to keep current character visible
        cursor_pos = len(self.typed)
        if cursor_pos < len(self.current_text):
            # Calculate the text index for the current character
            line_col = self.text_canvas.index(f"1.0 + {cursor_pos} chars")
            self.text_canvas.see(line_col)

        self.text_canvas.configure(state="disabled")

    def _update_stats(self):
        if not self.start_time:
            return

        elapsed_min = (time.time() - self.start_time) / 60.0
        if elapsed_min > 0:
            wpm = int((len(self.typed) / 5.0) / elapsed_min)
            self.wpm_var.set(str(wpm))

        total = len(self.typed) + self.errors
        acc = round((len(self.typed) / total) * 100) if total > 0 else 100
        self.acc_var.set(f"{acc}%")
        self.streak_var.set(str(self.streak))
        self.score_var.set(str(self.score))
        self.combo_var.set(f"x{self.combo}")

    def _trigger_visual_effect(self, correct):
        """Simple visual feedback for typing."""
        if correct:
            if self.combo > 5:
                self.combo_label.config(fg=ACCENT)
            else:
                self.combo_label.config(fg=MUTED)
        else:
            # Flash red on error (very brief)
            self.root.configure(bg=ERROR_BG)
            self.root.after(50, lambda: self.root.configure(bg=BG))
            self.combo_label.config(fg=ERROR)

    def _on_key(self, event):
        if self.is_finished:
            return

        # Handle backspace
        if event.keysym == "BackSpace":
            if self.typed:
                self.typed = self.typed[:-1]
                self._render_text()
                if len(self.typed) < len(self.current_text):
                    self._highlight_key(self.current_text[len(self.typed)])
            return

        # Ignore modifier keys, arrows, etc.
        char = event.char
        if not char or len(char) != 1 or ord(char) < 32:
            return

        if len(self.typed) >= len(self.current_text):
            return

        # Start timer on first keypress
        if not self.start_time:
            self.start_time = time.time()
            self._start_ai()

        expected = self.current_text[len(self.typed)]

        if char == expected:
            self.streak += 1
            self.combo += 1
            self.score += 10 + (self.combo * 2) # Combo bonus
            if self.streak > self.max_streak:
                self.max_streak = self.streak
            if self.combo > self.max_combo:
                self.max_combo = self.combo
            self._trigger_visual_effect(True)
        else:
            self.streak = 0
            self.combo = 0
            self.errors += 1
            self.score = max(0, self.score - 50) # Penalty
            self._trigger_visual_effect(False)

        self.typed += char
        self._render_text()
        self._update_stats()

        # Highlight next key or finish
        if len(self.typed) < len(self.current_text):
            self._highlight_key(self.current_text[len(self.typed)])
            self._update_progress_bars()
        else:
            self._highlight_key(None)
            self._update_progress_bars()
            self._finish_game()

    def _finish_game(self):
        self.is_finished = True
        self._show_modal()

    def _show_modal(self):
        """Show a session-complete overlay."""
        self.modal_overlay = tk.Frame(self.root, bg="#000000")
        self.modal_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Semi-transparent effect via dark bg
        self.modal_overlay.configure(bg="#111827")

        # Center modal
        modal = tk.Frame(self.modal_overlay, bg=SECONDARY_BG, highlightbackground=BORDER,
                         highlightthickness=2, padx=30, pady=25)
        modal.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(modal, text="Session Complete!", font=self.font_modal_title,
                 fg=WHITE, bg=SECONDARY_BG).pack(pady=(0, 20))

        stats_row = tk.Frame(modal, bg=SECONDARY_BG)
        stats_row.pack(pady=(0, 20))

        for label_text, value in [("Final WPM", self.wpm_var.get()), ("Accuracy", self.acc_var.get()), ("Score", self.score_var.get())]:
            card = tk.Frame(stats_row, bg=BG, padx=25, pady=15)
            card.pack(side="left", padx=8)
            tk.Label(card, text=label_text, font=self.font_modal_label,
                     fg=MUTED, bg=BG).pack()
            tk.Label(card, text=value, font=self.font_modal_value,
                     fg=ACCENT, bg=BG).pack()
        
        # Result message
        result_msg = "Session Complete!"
        if self.ai_mode.get() != "Solo":
            if self.ai_finished and len(self.typed) < len(self.current_text):
                result_msg = "AI Won! Keep practicing."
                modal_color = ERROR
            elif not self.ai_finished and len(self.typed) >= len(self.current_text):
                result_msg = "Victory! You beat the AI."
                modal_color = ACCENT
            else:
                result_msg = "It's a tie!"
                modal_color = WHITE
            
            tk.Label(modal, text=result_msg, font=self.font_modal_label, 
                     fg=modal_color, bg=SECONDARY_BG).pack(pady=(0,10))

        btn = tk.Label(modal, text="  Play Again  ", font=self.font_btn,
                       fg=WHITE, bg=ACCENT, cursor="hand2", padx=20, pady=8)
        btn.pack(pady=(5, 0))
        btn.bind("<Button-1>", lambda e: self._restart())
        btn.bind("<Enter>", lambda e: btn.configure(bg=ACCENT_HOVER))
        btn.bind("<Leave>", lambda e: btn.configure(bg=ACCENT))

    def _restart(self):
        if self.modal_overlay:
            self.modal_overlay.place_forget()
            self.modal_overlay.destroy()
        self.load_game()

    def load_game(self):
        """Load a new game with random text."""
        self.typed = ""
        self.start_time = None
        self.errors = 0
        self.streak = 0
        self.max_streak = 0
        self.is_finished = False

        self.wpm_var.set("0")
        self.acc_var.set("100%")
        self.streak_var.set("0")
        
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.score_var.set("0")
        self.combo_var.set("x0")

        # 30% chance to try Gutenberg API
        if random.random() < 0.3:
            self.current_text = "Loading..."
            self._render_text()
            thread = threading.Thread(target=self._load_from_api, daemon=True)
            thread.start()
        else:
            self.current_text = random.choice(STORIES)
            self._render_text()
            self._highlight_key(self.current_text[0])

        self.root.focus_force()

    def _load_from_api(self):
        text = fetch_gutenberg_text()
        if text:
            self.current_text = text
        else:
            self.current_text = random.choice(STORIES)

        # Update UI from main thread
        self.root.after(0, self._after_load)

    def _after_load(self):
        self._render_text()
        if self.current_text:
            self._highlight_key(self.current_text[0])
            self._update_progress_bars()

    def _on_ai_change(self):
        self.load_game()

    def _update_progress_bars(self):
        if not self.current_text: return
        
        # Player
        p_ratio = len(self.typed) / len(self.current_text)
        w = self.player_canvas.winfo_width()
        if w > 1:
            self.player_canvas.coords(self.player_rect, 0, 0, int(w * p_ratio), 10)
        
        # AI
        a_ratio = self.ai_progress / len(self.current_text)
        w_ai = self.ai_canvas.winfo_width()
        if w_ai > 1:
            self.ai_canvas.coords(self.ai_rect, 0, 0, int(w_ai * a_ratio), 10)

    def _start_ai(self):
        mode = self.ai_mode.get()
        if mode == "Solo": 
            return
        
        speeds = {"Easy": 25, "Normal": 50, "Hard": 85}
        self.ai_wpm = speeds.get(mode, 50)
        self.ai_progress = 0
        self.ai_running = True
        self.ai_finished = False
        self.ai_start_time = time.time()
        
        thread = threading.Thread(target=self._ai_loop, daemon=True)
        thread.start()

    def _ai_loop(self):
        while self.ai_running and not self.is_finished:
            if not self.current_text:
                time.sleep(0.1)
                continue
            
            # WPM to characters per second: (WPM * 5) / 60
            chars_per_sec = (self.ai_wpm * 5) / 60
            time.sleep(1.0 / chars_per_sec)
            
            if not self.ai_running or self.is_finished: break
            
            self.ai_progress += 1
            self.root.after(0, self._update_progress_bars)
            
            if self.ai_progress >= len(self.current_text):
                self.ai_finished = True
                self.ai_running = False
                break

    def _finish_game(self):
        self.is_finished = True
        self.ai_running = False
        self._show_modal()


def main():
    root = tk.Tk()
    # Try to set icon if available
    try:
        import os
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "nano_banana.png")
        if os.path.exists(icon_path):
            img = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, img)
    except Exception:
        pass

    QwertyMasterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
