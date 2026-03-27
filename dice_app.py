import streamlit as st
import random
import sqlite3
from datetime import datetime
import os

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(page_title="Dice Game 🎲", layout="centered")

# ---------------- DATABASE SETUP ---------------- #
conn = sqlite3.connect("dice.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    score INTEGER,
    result TEXT,
    date TEXT
)
""")
conn.commit()

# ---------------- FUNCTIONS ---------------- #

def roll_dice(num_dice):
    return [random.randint(1, 6) for _ in range(num_dice)]

def save_score(name, score, result):
    c.execute("INSERT INTO scores (name, score, result, date) VALUES (?, ?, ?, ?)",
              (name, score, result, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

def get_leaderboard():
    c.execute("SELECT name, score, result, date FROM scores ORDER BY score DESC LIMIT 10")
    return c.fetchall()

# Dice emoji fallback (if no images folder)
dice_emoji = {
    1: "⚀",
    2: "⚁",
    3: "⚂",
    4: "⚃",
    5: "⚄",
    6: "⚅"
}

def show_dice(dice):
    cols = st.columns(len(dice))
    for i, value in enumerate(dice):
        image_path = f"images/dice{value}.png"
        if os.path.exists(image_path):
            cols[i].image(image_path, width=80)
        else:
            cols[i].markdown(f"<h1 style='text-align:center'>{dice_emoji[value]}</h1>", unsafe_allow_html=True)

# ---------------- SESSION STATE ---------------- #
if "total_score" not in st.session_state:
    st.session_state.total_score = 0

if "roll_count" not in st.session_state:
    st.session_state.roll_count = 0

# ---------------- UI ---------------- #

st.title("🎲 Dice Rolling Game")

name = st.text_input("👤 Enter your name")

num_dice = st.slider("🎯 Select number of dice", 1, 5, 2)

st.write(f"🎮 Total Score: {st.session_state.total_score}")
st.write(f"🔄 Roll Count: {st.session_state.roll_count}")

# ---------------- GAME ---------------- #

if st.button("🎲 Roll Dice"):
    dice = roll_dice(num_dice)
    total = sum(dice)

    st.session_state.roll_count += 1

    # Show Dice
    show_dice(dice)

    st.subheader(f"➕ Sum of Dice: {total}")

    # Win / Lose Logic
    if total >= 15:
        result = "Win 🎉"
        st.success("🎉 You Win!")
        st.session_state.total_score += 10
    else:
        result = "Lose ❌"
        st.error("❌ You Lose!")
        st.session_state.total_score -= 5

    st.write(f"🏆 Updated Score: {st.session_state.total_score}")

    # Save to database
    if name.strip():
        save_score(name, st.session_state.total_score, result)

# ---------------- RESET BUTTON ---------------- #
if st.button("🔄 Reset Game"):
    st.session_state.total_score = 0
    st.session_state.roll_count = 0
    st.success("Game Reset!")

# ---------------- LEADERBOARD ---------------- #

st.subheader("🏆 Leaderboard (Top 10 Players)")

leaderboard = get_leaderboard()

if leaderboard:
    for i, row in enumerate(leaderboard, start=1):
        st.write(f"{i}. 👤 {row[0]} | Score: {row[1]} | {row[2]} | 📅 {row[3]}")
else:
    st.info("No scores yet. Play the game!")

# ---------------- FOOTER ---------------- #
st.markdown("---")
st.markdown("🚀 Built with Streamlit | 🎲 Dice Game Project")