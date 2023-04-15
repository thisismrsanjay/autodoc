
# AUTODOC🤖

## Summary 📝

The Autodoc project aims to create a seamless and automated solution for generating documentation for GitHub repositories. The project parses individual GitHub repositories, extracts the code, and sends it to OpenAI using the OpenAI API. The API processes the code to generate a global dictionary and subsequently, a comprehensive documentation. In addition, an extension has been developed to make the documentation process even more effortless for users.

## Project Objectives ✅



- Automate the process of generating documentation for GitHub repositories.
- Facilitate code understanding and maintenance by providing accurate and organized documentation.
- Save time and effort for developers who manually create and update documentation.
- Enhance collaboration among developers by offering well-documented code.

## Workflow 👷

### a.  Repository Parsing

- The Autodoc system accesses the target GitHub repository.
- It iterates through the repository's files and folders, identifying and extracting the code.

### b. Code Processing and Analysis

- The extracted code is sent to OpenAI using the OpenAI API.
- The API analyzes the code, generating a global dictionary containing relevant information about classes, functions, and variables.

```bash
code_structure = {
    "modules": {
        "module1": {
            "classes": {
                "Class1": {
                    "methods": {
                        "method1": {"params": ..., "return_type": ...},
                        "method2": {"params": ..., "return_type": ...},
                    }
                },
                "Class2": {
                    "methods": ...
                }
            },
            "functions": {
                "function1": {"params": ..., "return_type": ...},
                "function2": {"params": ..., "return_type": ...},
            }
        },
        "module2": ...
    }
}
```
    


### c. Documentation Generation
- Based on the global dictionary, the Autodoc system creates a well-structured and informative documentation.
- The generated documentation is saved in a user-friendly format, such as Markdown or HTML.

### d. Autodoc Extension

- The Autodoc extension streamlines the documentation process by enabling users to generate documentation directly from their GitHub repositories.
- Users can install the extension on their preferred web browser and easily initiate the documentation generation with a single click.



## Installation ⚙️

- Download the extension's source code from this GitHub repository

- Extract the ZIP file
- Enable "Developer Mode" in Google Chrome
- Load the extracted extension in Chrome
    -  On the Extensions page, click on the "Load unpacked" button, which should now be visible after enabling Developer mode.
    -  In the file browser that opens, navigate to the folder containing the extracted extension files from the GitHub repository.
    -  Select the folder and click on "Open" or "Select Folder" (depending on your operating system).

## How to use 👨‍💻

- Release 1 
    - Select the code you want to make documentation
    - Right click (as the extension is installed it will have a prompt  **create documentation** )

- Release 2 
    - Go to repo page 
    - Right click create documentation