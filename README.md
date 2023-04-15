similar to readme a popup


const { Configuration, OpenAIApi } = require("openai");
    const configuration = new Configuration({
        apiKey: "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",
    });
    const openai = new OpenAIApi(configuration);
    const response = async function getCompletion() {
        const response = await openai.createCompletion({
          model: "text-davinci-003",
          prompt: "what is 2 + 2",
          temperature: 0,
          max_tokens: 7,
        });
        return response.choices[0].text;
      }
    console.log(response)





// parsing entire github repo 


take all files read them one by one make a global dictionary 
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
// breaking the code into smaller chunks
