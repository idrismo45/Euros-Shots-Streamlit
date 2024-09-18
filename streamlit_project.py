import json
import pandas as pd
import streamlit as st
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Streamlit App Title and Logo
st.image('logo.jpg', width=150)  # Add the Euros logo
st.markdown("<h1 style='text-align: center; color: blue;'>Euros 2024 Shot Map</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: gray;'>Filter to any team/player to see all their shots taken!</h2>", unsafe_allow_html=True)

# Load the data
df = pd.read_csv('euros_2024_shot_map.csv')
df = df[df['type'] == 'Shot'].reset_index(drop=True)
df['location'] = df['location'].apply(json.loads)

# Streamlit Select Boxes for user inputs
team = st.selectbox("Select a team", df['team'].sort_values().unique(), index=None)

if team:
    player = st.selectbox("Select a player", df[df['team'] == team]['player'].sort_values().unique(), index=None)

    def filter_data(df: pd.DataFrame, team: str, player: str):
        if team:
            df = df[df['team'] == team]
        if player:
            df = df[df['player'] == player]
        return df

    filtered_df = filter_data(df, team, player)

    # Pitch setup with natural green color and white lines
    pitch = VerticalPitch(pitch_color='grass', line_color='white', half=True)
    fig, ax = pitch.draw(figsize=(12, 7))

    # Manually set pitch and line colors
    ax.set_facecolor('green')  # Set pitch color
    for spine in ax.spines.values():
        spine.set_edgecolor('white')  # Set line color

    def plot_shots(df, ax, pitch):
        # Track which colors are used
        used_colors = set()

        for x in df.to_dict(orient='records'):
            if x['shot_type'] == 'Penalty':
                continue  # Skip penalty shots
            
            # Determine color based on shot outcome and type
            color = 'green' if x['shot_outcome'] == 'Goal' else 'red'
            # Further differentiate by shot type
            if x['shot_type'] == 'Open Play':
                color = 'blue' if x['shot_outcome'] == 'Goal' else 'orange'
            elif x['shot_type'] == 'Corner':
                color = 'cyan' if x['shot_outcome'] == 'Goal' else 'magenta'
            elif x['shot_type'] == 'Free Kick':
                color = 'yellow' if x['shot_outcome'] == 'Goal' else 'gray'
            
            used_colors.add(color)

            pitch.scatter(
                x=float(x['location'][0]),
                y=float(x['location'][1]),
                ax=ax,
                s=300,  # Reduced size for all markers
                color=color,
                edgecolors='black',
                alpha=0.8,
                zorder=2 if x['shot_outcome'] == 'Goal' else 1
            )
            # Annotate shots
            ax.annotate(
                x['player'],
                (float(x['location'][0]), float(x['location'][1])),
                textcoords="offset points",
                xytext=(0,10),
                ha='center',
                fontsize=8
            )
        
        return used_colors

    used_colors = plot_shots(filtered_df, ax, pitch)

    # Define all possible colors and their labels
    color_labels = {
        'blue': 'Open Play Goal',
        'orange': 'Open Play Miss',
        'cyan': 'Corner Goal',
        'magenta': 'Corner Miss',
        'yellow': 'Free Kick Goal',
        'gray': 'Free Kick Miss'
    }

    # Filter the legend elements based on used colors
    legend_elements = [patches.Patch(color=color, label=label) for color, label in color_labels.items() if color in used_colors]

    # Create an inset axis for the legend
    legend_ax = fig.add_axes([0.85, 0.15, 0.1, 0.7])  # Adjust these values as needed
    legend_ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))
    legend_ax.axis('off')  # Turn off axis for the legend

    # Show the plot
    st.pyplot(fig)

    # Penalty Summary
    penalties_df = filtered_df[filtered_df['shot_type'] == 'Penalty']

    if not penalties_df.empty:
        st.subheader("Penalty Summary")
        
        # Separate penalties into regular and shootout
        regular_penalties = penalties_df[penalties_df['minute'] < 120]
        shootout_penalties = penalties_df[penalties_df['minute'] >= 120]

        if not regular_penalties.empty:
            st.write("### Regular Penalties:")
            for index, row in regular_penalties.iterrows():
                outcome = "Scored" if row['shot_outcome'] == 'Goal' else "Missed"
                st.write(f"Player: {row['player']}, Minute: {row['minute']}, Outcome: {outcome}")

        if not shootout_penalties.empty:
            st.write("### Shootout Penalties:")
            for index, row in shootout_penalties.iterrows():
                outcome = "Scored" if row['shot_outcome'] == 'Goal' else "Missed"
                st.write(f"Player: {row['player']}, Outcome: {outcome}")
else:
    st.write("Please select a team and player to view the data.")



