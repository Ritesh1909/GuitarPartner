import random
import streamlit as st

# Chord Dictionaries
power_chords = {
    "C": ["C5", "D5", "E5", "F5", "G5", "A5", "B5"],
    "G": ["G5", "A5", "B5", "C5", "D5", "E5", "F#5"],
    "D": ["D5", "E5", "F#5", "G5", "A5", "B5", "C#5"],
    "A": ["A5", "B5", "C#5", "D5", "E5", "F#5", "G#5"],
    "E": ["E5", "F#5", "G#5", "A5", "B5", "C#5", "D#5"],
    "F": ["F5", "G5", "A5", "Bb5", "C5", "D5", "E5"],
    "B": ["B5", "C#5", "D#5", "E5", "F#5", "G#5", "A#5"]
}

seventh_chords_major = {
    "C": ["Cmaj7", "Dm7", "Em7", "Fmaj7", "G7", "Am7", "Bdim7"],
    "G": ["Gmaj7", "Am7", "Bm7", "Cmaj7", "D7", "Em7", "F#dim7"],
    "D": ["Dmaj7", "Em7", "F#m7", "Gmaj7", "A7", "Bm7", "C#dim7"],
    "A": ["Amaj7", "Bm7", "C#m7", "Dmaj7", "E7", "F#m7", "G#dim7"],
    "E": ["Emaj7", "F#m7", "G#m7", "Amaj7", "B7", "C#m7", "D#dim7"],
    "F": ["Fmaj7", "Gm7", "Am7", "Bbmaj7", "C7", "Dm7", "Edim7"],
    "B": ["Bmaj7", "C#m7", "D#m7", "Emaj7", "F#7", "G#m7", "A#dim7"]
}

extended_chords = {
    "C": ["C9", "C11", "C13", "Cadd9"],
    "G": ["G9", "G11", "G13", "Gadd9"],
    "D": ["D9", "D11", "D13", "Dadd9"],
    "A": ["A9", "A11", "A13", "Aadd9"],
    "E": ["E9", "E11", "E13", "Eadd9"],
    "F": ["F9", "F11", "F13", "Fadd9"],
    "B": ["B9", "B11", "B13", "Badd9"]
}

dim_aug_chords = {
    "C": ["Cdim", "Caug", "Cdim7"],
    "G": ["Gdim", "Gaug", "Gdim7"],
    "D": ["Ddim", "Daug", "Ddim7"],
    "A": ["Adim", "Aaug", "Adim7"],
    "E": ["Edim", "Eaug", "Edim7"],
    "F": ["Fdim", "Faug", "Fdim7"],
    "B": ["Bdim", "Baug", "Bdim7"]
}

# Build Transition Matrix
def build_transition_matrix(chord_list):
    matrix = {}
    for chord in chord_list:
        next_chords = chord_list.copy()
        next_chords.remove(chord)
        matrix[chord] = {ch: 1 / len(next_chords) for ch in next_chords}
    return matrix

# Generate Chord Progression
def generate_chord_progression(
    key: str,
    mode: str,
    num_chords: int,
    training_type: str,
    difficulty_level: str = None,
    selected_families: list = None
):
    """
    Generates a chord progression based on inputs.

    :param key: The tonal center (e.g., "C", "G", etc.).
    :param mode: Mode (e.g., "Major", "Minor").
    :param num_chords: Number of chords in the progression.
    :param training_type: Either "difficulty" or "chord family".
    :param difficulty_level: If training_type == "difficulty", one of ["Beginner", "Intermediate", "Expert"].
    :param selected_families: If training_type == "chord family", list of chord families the user chose.
    :return: A list of chords representing the generated progression.
    """
    chord_list = []

    # Handle "difficulty" training type
    if training_type == "difficulty":
        if difficulty_level == "Beginner":
            chord_list = power_chords[key]
        elif difficulty_level == "Intermediate":
            chord_list = power_chords[key] + seventh_chords_major[key]
        elif difficulty_level == "Expert":
            chord_list = (
                seventh_chords_major[key]
                + extended_chords[key]
                + dim_aug_chords[key]
            )

    # Handle "chord family" training type
    elif training_type == "chord family":
        if not selected_families:
            raise ValueError("Please select at least one chord family.")

        chord_family_mapping = {
            "Power Chords": power_chords,
            "Seventh Chords Major": seventh_chords_major,
            "Extended Chords": extended_chords,
            "Diminished & Augmented Chords": dim_aug_chords
        }

        # Gather chords for the SINGLE key the user picked, across all chosen families
        for fam in selected_families:
            chord_list.extend(chord_family_mapping[fam][key])

    if not chord_list:
        raise ValueError("No valid chords found for the selected inputs.")

    # Build transition matrix and create progression
    transition_matrix = build_transition_matrix(chord_list)
    progression = [random.choice(chord_list)]

    for _ in range(num_chords - 1):
        current_chord = progression[-1]
        # Weighted random choice based on equal probabilities
        next_chord = random.choices(
            list(transition_matrix[current_chord].keys()),
            weights=transition_matrix[current_chord].values()
        )[0]
        progression.append(next_chord)

    return progression

# Streamlit UI
if __name__ == "__main__":
    st.title("🎸 Guitar Chord Progression Generator")

    # The user picks ONE key (for both difficulty or chord family)
    key = st.selectbox("Select Key:", ["C", "G", "D", "A", "E", "F", "B"])
    mode = st.selectbox("Select Mode:", ["Major", "Minor"])
    num_chords = st.slider("Number of Chords", 4, 16, 8)

    training_type = st.radio("Training Type", ["difficulty", "chord family"])

    difficulty_level = None
    selected_families = []

    # If difficulty is selected, show difficulty level
    if training_type == "difficulty":
        difficulty_level = st.selectbox("Select Difficulty Level:", ["Beginner", "Intermediate", "Expert"])

    # If chord family is selected, show chord families multi-select
    if training_type == "chord family":
        chord_family_options = [
            "Power Chords",
            "Seventh Chords Major",
            "Extended Chords",
            "Diminished & Augmented Chords"
        ]
        selected_families = st.multiselect(
            "Select Chord Families:",
            chord_family_options
        )

    # Generate button
    if st.button("Generate Progression"):
        try:
            progression = generate_chord_progression(
                key=key,
                mode=mode,
                num_chords=num_chords,
                training_type=training_type,
                difficulty_level=difficulty_level,
                selected_families=selected_families
            )
            st.success(f"Generated Chord Progression: {progression}")
        except ValueError as e:
            st.error(str(e))
