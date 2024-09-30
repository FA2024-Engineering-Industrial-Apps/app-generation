import streamlit as st

def get_publish_form():
    # Create a form object using st.form with a specific key
    form = st.form(key="my_form")

    # Add form fields
    ie_user = form.text_input("IE_USER")
    ie_pass = form.text_input("IE_PASS", type="password")
    webaddress = form.text_input("WEBADDRESS")
    app_name = form.text_input("app_name")
    app_description = form.text_input("app_description")
    icon = form.file_uploader("Upload app icon", type=['png', 'jpg', 'jpeg'])
    version_number = form.text_input("version_number")

    # Dropdown for category with two options: "Retail" and "Other"
    category = form.selectbox("category", ["Retail", "Other"])

    # Add the submit button inside the form object
    submit_button = form.form_submit_button(label="Submit")
    return form


