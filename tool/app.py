import streamlit as st  
import documentation as doc

st.title = "AutoDoc"

uploaded_file = st.file_uploader("upload test file")


if uploaded_file is not None:
    content = uploaded_file.read().decode(errors='ignore')
    response = doc.ask(f"read the text it has summary of multiple files of a project make a comprehensive documentation README.md for it it can contain installation guide, use of file ,important functions in it, the complete code summary explaining each file, technologies used,where project can be used ,etc  be creative and add  to it {content}\n\n ")
    #st.markdown("""----""")
    #st.subheader("Response")
    #st.text(response)
    st.markdown("""----""")
    st.subheader("Preview")
    st.markdown(response)