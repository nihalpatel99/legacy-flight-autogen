import streamlit as st
# Title of the app
st.title("Welcome to Streamlit!")
# Displaying a header and subheader
st.header("This is a Header")
st.subheader("This is a Subheader")
# Displaying plain text
st.text("Streamlit makes building web apps easy!")
# Adding a markdown text
st.markdown("### Markdown Example: Level 3 Header")
# Adding a success message
st.success("This is a success message!")
# Adding a checkbox
if st.checkbox("Show/Hide"):
   st.text("Checkbox is checked!")
# Adding a radio button
status = st.radio("Select an option:", ['Option 1', 'Option 2'])
if status == 'Option 1':
   st.success("You selected Option 1")
else:
   st.success("You selected Option 2")
# Adding a slider
level = st.slider("Choose a level", min_value=1, max_value=5)
st.write(f"Selected level: {level}")
# Adding a button
if st.button("Click Me"):
   st.text("Button clicked!")