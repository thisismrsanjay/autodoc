import streamlit as st  
import documentation as doc
import zipfile
import io
import os

st.title("autodoc- document generator for github")

uploaded_file = st.file_uploader("Upload ZIP file")

# Define the file extensions to include and the max file size in KB
include_file_extensions = ['.py', '.js', '.txt','.md']
max_file_size_kb = 4

if uploaded_file is not None:
    with zipfile.ZipFile(io.BytesIO(uploaded_file.read()), 'r') as zipped_files:
        readme_text = ""
        for filename in zipped_files.namelist():
            if not filename.endswith('/') and os.path.splitext(filename)[1] in include_file_extensions:  # Ignore directories and files with other extensions
                with zipped_files.open(filename, 'r') as file:
                    content = file.read().decode()
                    # Only process the file if its size is less than the max size
                    if len(content) <= max_file_size_kb * 1024:  # Convert size to bytes
                        response = doc.ask(f"Read the code and give the short  documentation for it keep important functionality, and its intended use maybe important functions, classes  but no programs in documentation \n\n {content}")
                        readme_text += f"## {filename}\n\n{response}\n\n"

    # Write the readme_text to a file
    with open("readme_output.txt", "w") as file:
        file.write(readme_text)

    st.markdown("""----""")
    st.subheader("Response")
    st.text(readme_text)
    st.markdown("""----""")
    st.subheader("Preview")
    st.markdown(readme_text)





