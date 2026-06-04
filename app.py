import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION ---
DB_FILE = "panini_collection.csv"
TOTAL_CARDS = 630  # Updated to match the massive 630-card standard set size

st.set_page_config(page_title="Panini Adrelyn XL Tracker", page_icon="⚽", layout="wide")


# --- DATA STORAGE HANDLERS ---
def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # If the existing file was generated with a different card limit, expand or recreate it
        if len(df) != TOTAL_CARDS:
            df = create_new_db()
    else:
        df = create_new_db()
    return df


def create_new_db():
    df = pd.DataFrame({
        "Card Number": range(1, TOTAL_CARDS + 1),
        "Owned": [False] * TOTAL_CARDS,
        "Quantity": [0] * TOTAL_CARDS
    })
    df.to_csv(DB_FILE, index=False)
    return df


def save_data(df):
    df.to_csv(DB_FILE, index=False)


# Load data into session state to keep it persistent during user interaction
if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# --- APP HEADER ---
st.title("⚽ Panini Adrelyn XL World Cup Tracker")
st.subheader("Plan your swaps and track what's missing")

# --- DASHBOARD METRICS ---
owned_count = df["Owned"].sum()
missing_count = TOTAL_CARDS - owned_count
completion_rate = (owned_count / TOTAL_CARDS) * 100

col1, col2, col3 = st.columns(3)
col1.metric("Cards Owned", f"{owned_count} / {TOTAL_CARDS}")
col2.metric("Cards Missing", missing_count)
col3.metric("Completion Rate", f"{completion_rate:.1f}%")

st.progress(completion_rate / 100)
st.markdown("---")

# --- APP TABS ---
tab_update, tab_missing, tab_all = st.tabs(["✏️ Update Collection", "🔍 Missing List", "📋 View All"])

# TAB 1: UPDATE COLLECTION
with tab_update:
    st.header("Quick Log")
    st.write("Enter card numbers below to toggle them as owned.")

    # Batch entry input box
    input_numbers = st.text_input("Enter Card Numbers (separated by commas, e.g., 5, 12, 45, 620):")

    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("Add These Cards", type="primary"):
        if input_numbers:
            try:
                # Parse inputs, strip spaces, filter out non-digits or out-of-bounds numbers
                nums = [int(n.strip()) for n in input_numbers.split(",") if n.strip().isdigit()]
                valid_nums = [n for n in nums if 1 <= n <= TOTAL_CARDS]

                # Update DataFrame
                df.loc[df["Card Number"].isin(valid_nums), "Owned"] = True
                df.loc[df["Card Number"].isin(valid_nums), "Quantity"] = 1

                save_data(df)
                st.success(f"Successfully added cards: {valid_nums}")
                st.rerun()
            except Exception as e:
                st.error("Error processing input. Ensure it's a comma-separated list of numbers.")

    if col_btn2.button("Remove These Cards"):
        if input_numbers:
            try:
                nums = [int(n.strip()) for n in input_numbers.split(",") if n.strip().isdigit()]
                valid_nums = [n for n in nums if 1 <= n <= TOTAL_CARDS]

                df.loc[df["Card Number"].isin(valid_nums), "Owned"] = False
                df.loc[df["Card Number"].isin(valid_nums), "Quantity"] = 0

                save_data(df)
                st.success(f"Removed cards: {valid_nums}")
                st.rerun()
            except Exception as e:
                st.error("Error processing input.")

# TAB 2: MISSING LIST
with tab_missing:
    st.header("❌ Cards You Still Need")
    missing_df = df[df["Owned"] == False]["Card Number"].tolist()

    if not missing_df:
        st.balloons()
        st.success("🎉 Incredible! Your collection is 100% complete!")
    else:
        # Format as a clean, copy-pasteable string for trading groups
        missing_str = ", ".join(map(str, missing_df))
        # FIXED: Changed st.textarea to st.text_area
        st.text_area("Copy/Paste your missing list:", value=missing_str, height=150)

        # Display as a grid
        st.write("### Missing Grid Visualizer")
        st.dataframe(df[df["Owned"] == False][["Card Number"]], hide_index=True, use_container_width=True)

# TAB 3: VIEW ALL (INTERACTIVE TABLE)
with tab_all:
    st.header("📋 Full Checklist")
    st.write("You can directly check or uncheck boxes in the table below to update your collection.")

    # Interactive data editor
    edited_df = st.data_editor(
        df,
        column_config={
            "Card Number": st.column_config.NumberColumn("Card No.", disabled=True),
            "Owned": st.column_config.CheckboxColumn("Owned?"),
            "Quantity": st.column_config.NumberColumn("Duplicates/Qty", min_value=0, max_value=10)
        },
        disabled=["Card Number"],
        hide_index=True,
        use_container_width=True
    )

    # Automatically switch 'Owned' status if quantity changes via table edits
    edited_df.loc[edited_df["Quantity"] > 0, "Owned"] = True
    edited_df.loc[edited_df["Quantity"] == 0, "Owned"] = False

    # Save button for table edits
    if st.button("Save Table Changes"):
        st.session_state.df = edited_df
        save_data(edited_df)
        st.success("Changes saved successfully!")
        st.rerun()
