# student.py — Student Dashboard
# Features: browse quizzes, search, take quiz (JEE-style), review answers, see history.

import tkinter as tk
from tkinter import messagebox
import random
import db
import main

# ── Colors ────────────────────────────────────────────────
BG      = "#1e1e2e"   # dark background
PANEL   = "#2a2a3e"   # card / panel background
ACCENT  = "#7c3aed"   # purple
ENTRY   = "#12121c"   # input field background
FG      = "#ffffff"   # white text
DIM     = "#c0c0d0"   # dim / grey text
GREEN   = "#22c55e"   # correct / answered
RED     = "#ef4444"   # wrong / unanswered
YELLOW  = "#f59e0b"   # marked for review
ORANGE  = "#f97316"   # timer warning

# Palette cell colours (question status)
COLOR_NOT_VISITED = "#3b3b55"
COLOR_ANSWERED    = "#22c55e"
COLOR_MARKED      = "#f59e0b"
COLOR_SKIPPED     = "#ef4444"

# ── Fonts ──────────────────────────────────────────────────
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_BODY  = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 10)
FONT_TINY  = ("Segoe UI", 9)


# ── Helper Functions ───────────────────────────────────────

def make_btn(parent, text, command, color=ACCENT):
    """
    Creates a colored button that works on macOS.
    macOS ignores bg on tk.Button, so we use a Frame + Label instead.
    Clicking on either triggers the command.
    """
    frame = tk.Frame(parent, bg=color, cursor="hand2")
    label = tk.Label(frame, text=text, bg=color, fg=FG,
                     font=FONT_BODY, padx=10, pady=7)
    label.pack()
    frame.bind("<Button-1>", lambda e: command())
    label.bind("<Button-1>", lambda e: command())
    return frame


def center_window(win, width, height):
    """Opens a window centered on the screen."""
    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w - width)  // 2
    y = (screen_h - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


def seconds_to_mmss(total_seconds):
    """Converts seconds to a MM:SS string, e.g. 90 → '01:30'."""
    mins = total_seconds // 60
    secs = total_seconds % 60
    return f"{mins:02d}:{secs:02d}"


# ── Student Dashboard ──────────────────────────────────────

def show_student(user_id, username):
    """Main student window: quiz list, search bar, and attempt history."""

    root = tk.Tk()
    root.title("Student Dashboard")
    root.configure(bg=BG)
    center_window(root, 860, 600)

    # ── Top bar ───────────────────────────────────────────
    top_bar = tk.Frame(root, bg=ACCENT, pady=10)
    top_bar.pack(fill="x")

    tk.Label(top_bar, text=f"🎓  Student Portal  —  {username}",
             font=FONT_TITLE, bg=ACCENT, fg=FG).pack(side="left", padx=20)

    def do_logout():
        answer = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if answer:
            root.destroy()
            main.show_login()

    make_btn(top_bar, "⇠ Logout", do_logout, color="#5b21b6").pack(
        side="right", padx=16, pady=2)

    # ── Body: two columns ─────────────────────────────────
    body = tk.Frame(root, bg=BG)
    body.pack(fill="both", expand=True, padx=20, pady=12)

    # Left column: quiz list + search
    left_col = tk.Frame(body, bg=BG)
    left_col.pack(side="left", fill="both", expand=True, padx=(0, 12))

    tk.Label(left_col, text="Available Quizzes",
             font=("Segoe UI", 13, "bold"), bg=BG, fg=FG).pack(anchor="w")

    # Search bar row
    search_row = tk.Frame(left_col, bg=ENTRY)
    search_row.pack(fill="x", pady=(4, 2))
    tk.Label(search_row, text="🔍", bg=ENTRY, fg=DIM, font=FONT_BODY).pack(side="left", padx=6)
    search_var = tk.StringVar()
    tk.Entry(search_row, textvariable=search_var, bg=ENTRY, fg=FG,
             relief="flat", font=FONT_BODY, insertbackground=FG).pack(
             side="left", fill="x", expand=True, ipady=5)

    # IMPORTANT: Pack the button area BEFORE the listbox.
    # If we pack the listbox first with expand=True it will take all space
    # and the button will be invisible at the bottom.
    btn_area = tk.Frame(left_col, bg=BG)
    btn_area.pack(side="bottom", fill="x", pady=(6, 0))

    # Quiz listbox with scrollbar
    quiz_frame = tk.Frame(left_col, bg=ENTRY)
    quiz_frame.pack(fill="both", expand=True, pady=(2, 4))

    quiz_scroll = tk.Scrollbar(quiz_frame)
    quiz_scroll.pack(side="right", fill="y")

    quiz_listbox = tk.Listbox(quiz_frame, bg=ENTRY, fg=FG, font=FONT_BODY,
                              relief="flat", selectbackground=ACCENT,
                              activestyle="none", yscrollcommand=quiz_scroll.set)
    quiz_listbox.pack(fill="both", expand=True)
    quiz_scroll.config(command=quiz_listbox.yview)

    # These lists track what is shown in the listbox
    all_quizzes   = []   # every quiz from the database
    shown_quizzes = []   # quizzes currently displayed (after search filter)

    def refresh_quiz_list(*args):
        """Filter quizzes by search text and repopulate the listbox."""
        search_term = search_var.get().strip().lower()
        shown_quizzes.clear()
        quiz_listbox.delete(0, tk.END)
        for quiz in all_quizzes:
            # quiz[1] is the title
            if search_term in quiz[1].lower():
                shown_quizzes.append(quiz)
                quiz_listbox.insert(tk.END, f"  {quiz[1]}   ⏱ {quiz[2]} min")

    def load_quiz_list():
        """Fetch all quizzes from the database and display them."""
        all_quizzes.clear()
        all_quizzes.extend(db.get_all_quizzes())
        refresh_quiz_list()

    # Re-filter whenever the user types in the search box
    search_var.trace_add("write", refresh_quiz_list)
    load_quiz_list()

    # Right column: attempt history
    right_col = tk.Frame(body, bg=BG)
    right_col.pack(side="left", fill="both", expand=True)

    tk.Label(right_col, text="My History",
             font=("Segoe UI", 13, "bold"), bg=BG, fg=FG).pack(anchor="w")

    hist_frame = tk.Frame(right_col, bg=ENTRY)
    hist_frame.pack(fill="both", expand=True, pady=6)

    hist_scroll = tk.Scrollbar(hist_frame)
    hist_scroll.pack(side="right", fill="y")

    history_listbox = tk.Listbox(hist_frame, bg=ENTRY, fg=FG, font=FONT_SMALL,
                                 relief="flat", selectbackground=ACCENT,
                                 activestyle="none", yscrollcommand=hist_scroll.set)
    history_listbox.pack(fill="both", expand=True)
    hist_scroll.config(command=history_listbox.yview)

    def load_history():
        """Fetch and display the student's past quiz attempts."""
        history_listbox.delete(0, tk.END)
        rows = db.get_student_attempts(user_id)
        # Each row: (attempt_id, quiz_title, score, status)
        if not rows:
            history_listbox.insert(tk.END, "  No attempts yet.")
        else:
            for i, row in enumerate(rows):
                quiz_title = row[1]
                score      = row[2]   # this is the numeric score
                status     = row[3]   # "completed"
                history_listbox.insert(tk.END,
                    f"  {quiz_title}  →  {score} pts  [{status}]")
                # Green text if scored, grey otherwise
                color = GREEN if score > 0 else DIM
                history_listbox.itemconfig(i, fg=color)

    load_history()

    def start_quiz():
        """Start the selected quiz."""
        selection = quiz_listbox.curselection()
        if not selection:
            messagebox.showwarning("No quiz selected",
                                   "Please click a quiz from the list first.")
            return

        quiz      = shown_quizzes[selection[0]]
        questions = db.get_questions(quiz[0])   # quiz[0] is the quiz_id

        if not questions:
            messagebox.showinfo("Empty quiz", "This quiz has no questions yet.")
            return

        open_quiz_window(root, user_id, quiz, questions, on_done=load_history)

    # Place the Start Quiz button into the pre-reserved area at the bottom
    make_btn(btn_area, "▶  Start Quiz", start_quiz).pack(fill="x", ipady=2)

    root.mainloop()


# ── Quiz Window ────────────────────────────────────────────

def open_quiz_window(parent, user_id, quiz, questions, on_done):
    """
    Timed quiz window with:
    - JEE-style question palette  (colour-coded: answered / marked / skipped / not visited)
    - OMR progress bar            (fills green as questions are answered)
    - Mark for Review, Clear, navigation buttons
    - Auto-submit when time runs out
    - Warning if student tries to close the window mid-quiz
    """
    quiz_id    = quiz[0]
    quiz_title = quiz[1]
    time_limit = quiz[2]   # in minutes
    num_q      = len(questions)

    # Shuffle each question's options once at the start (option shuffling feature)
    # This randomises A/B/C/D order so students can't memorise positions
    options_for = {}   # {question_id: [list of option tuples]}
    for q in questions:
        opts = list(db.get_options(q[0]))
        random.shuffle(opts)
        options_for[q[0]] = opts

    # ── Create the window ─────────────────────────────────
    win = tk.Toplevel(parent)
    win.title(f"Quiz — {quiz_title}")
    win.configure(bg=BG)
    win.resizable(False, False)
    center_window(win, 960, 610)
    win.grab_set()   # prevent clicking on the parent window while quiz is open

    # ── State variables ───────────────────────────────────
    # We put these in lists so that nested functions can modify them
    current_index   = [0]   # which question we're currently showing
    student_answers = {}    # {question_id: selected_option_id}
    marked_set      = set() # indices of questions marked for review
    visited_set     = set() # indices of questions the student has seen
    secs_left       = [time_limit * 60]
    timer_job       = [None]            # stores the tk.after job ID
    selected_var    = tk.IntVar(value=-1)  # -1 means no option selected

    # ── Top bar ───────────────────────────────────────────
    topbar = tk.Frame(win, bg=PANEL, pady=8)
    topbar.pack(fill="x")
    tk.Label(topbar, text=quiz_title,
             font=("Segoe UI", 13, "bold"), bg=PANEL, fg=FG).pack(side="left", padx=16)

    timer_text  = tk.StringVar(value=seconds_to_mmss(secs_left[0]))
    timer_label = tk.Label(topbar, textvariable=timer_text,
                           font=("Segoe UI", 13, "bold"), bg=PANEL, fg=GREEN)
    timer_label.pack(side="right", padx=16)

    # ── Main layout: left pane + right palette ────────────
    main_area = tk.Frame(win, bg=BG)
    main_area.pack(fill="both", expand=True)

    # Left pane: question card + navigation
    left_pane = tk.Frame(main_area, bg=BG)
    left_pane.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=10)

    # "Question X / N" label
    q_progress_var = tk.StringVar()
    tk.Label(left_pane, textvariable=q_progress_var,
             font=FONT_TINY, bg=BG, fg=DIM).pack(anchor="w")

    # OMR progress bar: fills green based on how many questions are answered
    progress_canvas = tk.Canvas(left_pane, height=12, bg="#2d2d45",
                                highlightthickness=0)
    progress_canvas.pack(fill="x", pady=(2, 6))

    def draw_progress_bar():
        """Redraw the progress bar to show answered questions."""
        answered = sum(1 for q in questions if student_answers.get(q[0], -1) != -1)
        progress_canvas.delete("all")
        total_w = progress_canvas.winfo_width()
        if total_w < 2:
            return
        fill_w = int(total_w * answered / num_q)
        if fill_w > 0:
            progress_canvas.create_rectangle(0, 0, fill_w, 12, fill=GREEN, outline="")
        label = f"{answered} / {num_q} answered"
        progress_canvas.create_text(total_w // 2, 6, text=label,
                                    fill=FG, font=("Segoe UI", 8, "bold"))

    # When the canvas first appears or is resized, draw the bar
    progress_canvas.bind("<Configure>", lambda e: draw_progress_bar())

    # Question card (the big panel showing the question text and options)
    q_card = tk.Frame(left_pane, bg=PANEL, padx=20, pady=14)
    q_card.pack(fill="both", expand=True, pady=(0, 8))

    question_text_var = tk.StringVar()
    tk.Label(q_card, textvariable=question_text_var, font=FONT_BODY,
             bg=PANEL, fg=FG, wraplength=500, justify="left").pack(
             anchor="w", pady=(0, 10))

    options_frame  = tk.Frame(q_card, bg=PANEL)
    options_frame.pack(fill="x")
    option_widgets = []   # radio buttons for the current question

    # Navigation row (rebuilt each time we switch questions)
    nav_row = tk.Frame(left_pane, bg=BG)
    nav_row.pack(fill="x")

    # Right pane: question palette
    right_pane = tk.Frame(main_area, bg=PANEL, width=210)
    right_pane.pack(side="right", fill="y", padx=(0, 10), pady=10)
    right_pane.pack_propagate(False)   # don't shrink to fit contents

    tk.Label(right_pane, text="Question Palette",
             font=("Segoe UI", 10, "bold"), bg=PANEL, fg=FG).pack(pady=(10, 4))

    # Colour legend
    legend = tk.Frame(right_pane, bg=PANEL)
    legend.pack(padx=8, pady=(0, 4), fill="x")
    for dot_color, dot_label in [
        (COLOR_ANSWERED,    "Answered"),
        (COLOR_MARKED,      "Marked"),
        (COLOR_SKIPPED,     "Skipped"),
        (COLOR_NOT_VISITED, "Not Visited"),
    ]:
        row = tk.Frame(legend, bg=PANEL)
        row.pack(anchor="w", pady=1)
        tk.Label(row, text="●", fg=dot_color, bg=PANEL,
                 font=("Segoe UI", 12)).pack(side="left")
        tk.Label(row, text=f" {dot_label}", fg=DIM, bg=PANEL,
                 font=FONT_TINY).pack(side="left")

    tk.Frame(right_pane, bg="#444466", height=1).pack(fill="x", padx=8, pady=4)

    palette_grid    = tk.Frame(right_pane, bg=PANEL)
    palette_grid.pack(padx=8, pady=4, fill="both", expand=True)
    palette_buttons = []   # list of Label widgets used as palette cells

    # ── Palette helpers ───────────────────────────────────

    def get_cell_color(index):
        """Return the colour a palette cell should show based on question status."""
        q_id = questions[index][0]
        if index in marked_set:
            return COLOR_MARKED
        if student_answers.get(q_id, -1) != -1:
            return COLOR_ANSWERED
        if index in visited_set:
            return COLOR_SKIPPED
        return COLOR_NOT_VISITED

    def build_palette():
        """Build the numbered grid of palette cells."""
        for cell in palette_buttons:
            cell.destroy()
        palette_buttons.clear()
        for i in range(num_q):
            cell = tk.Label(palette_grid, text=str(i + 1),
                            bg=get_cell_color(i), fg=FG,
                            font=("Segoe UI", 9, "bold"),
                            width=3, relief="flat", cursor="hand2", pady=4)
            # Arrange in a 5-column grid
            cell.grid(row=i // 5, column=i % 5, padx=2, pady=2)
            # Clicking a cell jumps directly to that question
            cell.bind("<Button-1>", lambda e, idx=i: jump_to(idx))
            palette_buttons.append(cell)

    def refresh_palette():
        """Update all palette cell colours and redraw the progress bar."""
        for i, cell in enumerate(palette_buttons):
            cell.config(bg=get_cell_color(i))
        draw_progress_bar()

    # ── Navigation functions ──────────────────────────────

    def save_answer():
        """Store whatever is currently selected for the current question."""
        q_id = questions[current_index[0]][0]
        student_answers[q_id] = selected_var.get()

    def show_question(index):
        """Display the question at the given index."""
        # Remove the previous question's radio buttons
        for widget in option_widgets:
            widget.destroy()
        option_widgets.clear()

        visited_set.add(index)

        q      = questions[index]
        q_id   = q[0]
        q_text = q[2]

        q_progress_var.set(f"Question  {index + 1}  /  {num_q}")
        question_text_var.set(q_text)

        # Restore the student's previous answer (or -1 if not answered)
        selected_var.set(student_answers.get(q_id, -1))

        # Create one radio button for each option
        for opt in options_for[q_id]:
            opt_id   = opt[0]
            opt_text = opt[2]
            rb = tk.Radiobutton(
                options_frame, text=f"  {opt_text}",
                variable=selected_var, value=opt_id,
                bg=PANEL, fg=FG, activebackground=PANEL,
                selectcolor=ACCENT, font=FONT_BODY, anchor="w",
                command=refresh_palette   # update palette whenever an option is clicked
            )
            rb.pack(fill="x", pady=2)
            option_widgets.append(rb)

        # Rebuild navigation buttons
        for widget in nav_row.winfo_children():
            widget.destroy()

        make_btn(nav_row, "◀  Previous", go_previous,
                 color="#4b4b70").pack(side="left", padx=(0, 6))
        make_btn(nav_row, "🔖 Mark & Next", mark_and_next,
                 color=YELLOW).pack(side="left", padx=(0, 6))
        make_btn(nav_row, "✖ Clear", clear_answer,
                 color="#4b4b70").pack(side="left", padx=(0, 6))

        # Show "Submit" only on the last question
        if index == num_q - 1:
            make_btn(nav_row, "✔ Submit Quiz", confirm_submit,
                     color=GREEN).pack(side="right")
        else:
            make_btn(nav_row, "Next  ▶", go_next).pack(side="right")

        refresh_palette()

    def jump_to(index):
        """Jump directly to a specific question by clicking its palette cell."""
        save_answer()
        current_index[0] = index
        show_question(index)

    def go_next():
        save_answer()
        if current_index[0] < num_q - 1:
            current_index[0] += 1
            show_question(current_index[0])

    def go_previous():
        save_answer()
        if current_index[0] > 0:
            current_index[0] -= 1
            show_question(current_index[0])

    def mark_and_next():
        """Mark the current question for review and move to the next."""
        save_answer()
        marked_set.add(current_index[0])
        go_next()

    def clear_answer():
        """Remove the selected answer for the current question."""
        q_id = questions[current_index[0]][0]
        student_answers.pop(q_id, None)
        selected_var.set(-1)
        refresh_palette()

    # ── Submit ────────────────────────────────────────────

    def confirm_submit():
        """Show a summary popup before final submission."""
        save_answer()
        answered   = sum(1 for q in questions if student_answers.get(q[0], -1) != -1)
        unanswered = num_q - answered
        msg = (f"Answered  : {answered}\n"
               f"Marked    : {len(marked_set)}\n"
               f"Unanswered: {unanswered}\n\n"
               "Submit the quiz now?")
        if messagebox.askyesno("Confirm Submit", msg):
            do_submit()

    def do_submit():
        """Calculate the score, save to DB, close window, show result."""
        # Cancel the timer
        if timer_job[0]:
            win.after_cancel(timer_job[0])

        # Calculate score by checking which selected options are correct
        score = 0
        for q in questions:
            picked = student_answers.get(q[0], -1)
            for opt in options_for[q[0]]:
                if opt[0] == picked and opt[3] == 1:   # opt[3] is is_correct
                    score += q[3]                       # q[3] is marks for this question
                    break

        db.save_attempt(user_id, quiz_id, score)
        win.destroy()
        on_done()   # refresh the history list in the dashboard
        show_result_window(parent, quiz_title, score, questions,
                           options_for, student_answers)

    # ── Timer ─────────────────────────────────────────────

    def tick():
        """Count down by 1 second, update the timer label, and reschedule."""
        secs_left[0] -= 1
        timer_text.set(seconds_to_mmss(secs_left[0]))

        if secs_left[0] <= 30:
            timer_label.config(fg=RED)      # turn red at 30s
        elif secs_left[0] <= 60:
            timer_label.config(fg=ORANGE)   # turn orange at 60s

        if secs_left[0] <= 0:
            messagebox.showwarning("Time's up!", "Time is up! Submitting automatically.")
            do_submit()
            return   # don't schedule another tick

        # Schedule the next tick 1 second from now
        timer_job[0] = win.after(1000, tick)

    # ── Close warning ─────────────────────────────────────

    def on_window_close():
        """Warn the student if they try to close the quiz window."""
        answer = messagebox.askyesno(
            "Quit Quiz?",
            "Are you sure you want to quit?\n\nYour progress will NOT be saved.",
            icon="warning"
        )
        if answer:
            if timer_job[0]:
                win.after_cancel(timer_job[0])
            win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_window_close)

    # ── Start the quiz ────────────────────────────────────
    build_palette()
    show_question(0)
    tick()


# ── Result Window ──────────────────────────────────────────

def show_result_window(parent, quiz_title, score, questions, options_for, student_answers):
    """
    Shows the quiz result with a grade letter (S/A/B/C/D/F),
    percentage score,  visual score bar, and a Review button.
    """
    max_score = sum(q[3] for q in questions)   # q[3] is marks per question
    pct       = round(score / max_score * 100) if max_score > 0 else 0

    # Decide grade based on percentage
    if pct >= 90:
        grade, grade_color = "S", "#f59e0b"   # gold
    elif pct >= 75:
        grade, grade_color = "A", GREEN
    elif pct >= 60:
        grade, grade_color = "B", "#22d3ee"   # cyan
    elif pct >= 45:
        grade, grade_color = "C", "#a78bfa"   # light purple
    elif pct >= 35:
        grade, grade_color = "D", ORANGE
    else:
        grade, grade_color = "F", RED

    win = tk.Toplevel(parent)
    win.title("Quiz Result")
    win.configure(bg=BG)
    center_window(win, 420, 360)
    win.grab_set()

    # Purple header strip
    header = tk.Frame(win, bg=ACCENT, pady=10)
    header.pack(fill="x")
    tk.Label(header, text="✅  Quiz Complete!", font=FONT_TITLE, bg=ACCENT, fg=FG).pack()

    tk.Label(win, text=quiz_title, font=FONT_BODY, bg=BG, fg=DIM).pack(pady=(14, 2))

    # Grade badge + score side by side
    mid_row = tk.Frame(win, bg=BG)
    mid_row.pack(pady=6)

    tk.Label(mid_row, text=grade, font=("Segoe UI", 42, "bold"),
             bg=grade_color, fg=FG, width=3, pady=4).pack(side="left", padx=(0, 20))

    score_col = tk.Frame(mid_row, bg=BG)
    score_col.pack(side="left")
    tk.Label(score_col, text=f"{score} / {max_score}",
             font=("Segoe UI", 26, "bold"), bg=BG, fg=grade_color).pack(anchor="w")
    tk.Label(score_col, text=f"{pct}%  score",
             font=FONT_SMALL, bg=BG, fg=DIM).pack(anchor="w")

    # Visual score bar
    score_bar = tk.Canvas(win, height=10, bg="#2d2d45", highlightthickness=0)
    score_bar.pack(fill="x", padx=30, pady=(6, 0))
    win.update_idletasks()
    bar_w  = score_bar.winfo_width()
    fill_w = int(bar_w * pct / 100)
    if fill_w > 0:
        score_bar.create_rectangle(0, 0, fill_w, 10, fill=grade_color, outline="")

    # Buttons
    btn_row = tk.Frame(win, bg=BG)
    btn_row.pack(pady=16)

    make_btn(btn_row, "🔍 Review Answers",
             lambda: open_review_window(parent, quiz_title, questions,
                                        options_for, student_answers),
             color=ACCENT).pack(side="left", padx=6)

    make_btn(btn_row, "Close", win.destroy, color="#4b4b70").pack(side="left", padx=6)


# ── Review Window ──────────────────────────────────────────

def open_review_window(parent, quiz_title, questions, options_for, student_answers):
    """
    Scrollable review of all questions showing:
    ✅ correct answers,  ❌ wrong answers,  ⬜ skipped
    """
    win = tk.Toplevel(parent)
    win.title(f"Review — {quiz_title}")
    win.configure(bg=BG)
    center_window(win, 700, 580)

    tk.Label(win, text=f"📋  Answer Review — {quiz_title}",
             font=FONT_TITLE, bg=BG, fg=FG).pack(pady=(16, 4))

    # Scrollable canvas
    canvas    = tk.Canvas(win, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True, padx=(12, 0))

    inner = tk.Frame(canvas, bg=BG)
    win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    # Make inner frame as wide as the canvas
    def on_canvas_resize(event):
        canvas.itemconfig(win_id, width=event.width)
    canvas.bind("<Configure>", on_canvas_resize)

    # Mouse-wheel scrolling
    def on_scroll(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", on_scroll)

    # Build one card per question
    for i, q in enumerate(questions):
        q_id   = q[0]
        q_text = q[2]
        marks  = q[3]
        picked = student_answers.get(q_id, -1)
        opts   = options_for[q_id]

        # Find which option is correct
        correct_id = None
        for opt in opts:
            if opt[3] == 1:        # opt[3] is is_correct
                correct_id = opt[0]
                break

        is_correct = (picked == correct_id)

        # Card frame: green border if correct, red if wrong/skipped
        card = tk.Frame(inner, bg=PANEL, padx=14, pady=10,
                        highlightbackground=GREEN if is_correct else RED,
                        highlightthickness=2)
        card.pack(fill="x", pady=6, padx=8)

        # Question header with status icon
        if is_correct:
            icon = "✅"
        elif picked != -1:
            icon = "❌"
        else:
            icon = "⬜"

        tk.Label(card, text=f"{icon}  Q{i+1}. {q_text}",
                 font=FONT_BODY, bg=PANEL, fg=FG,
                 wraplength=580, justify="left").pack(anchor="w", pady=(0, 6))

        # Each option with colour-coded feedback
        for opt in opts:
            opt_id    = opt[0]
            opt_text  = opt[2]
            is_right  = (opt[3] == 1)    # is this the correct option?
            is_chosen = (opt_id == picked)

            if is_right and is_chosen:
                color, prefix = GREEN, "✅  "   # student chose correctly
            elif is_right and not is_chosen:
                color, prefix = GREEN, "👉  "   # correct answer student missed
            elif is_chosen and not is_right:
                color, prefix = RED,   "✖   "   # student's wrong choice
            else:
                color, prefix = DIM,   "      "  # neither correct nor chosen

            tk.Label(card, text=f"{prefix}{opt_text}",
                     font=FONT_SMALL, bg=PANEL, fg=color, anchor="w").pack(fill="x")

        # Marks earned
        earned = marks if is_correct else 0
        tk.Label(card, text=f"Marks: {earned} / {marks}",
                 font=("Segoe UI", 9, "bold"),
                 bg=PANEL, fg=GREEN if is_correct else RED).pack(anchor="e", pady=(6, 0))

    # Update scroll region after all cards are drawn
    inner.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    make_btn(win, "Close", win.destroy, color="#4b4b70").pack(pady=10)
