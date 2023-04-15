const axios = require("axios");

async function askChatGPT(question) {
  const apiKey = "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";
  const apiUrl = "https://api.openai.com/v1/engines/davinci/completions";

  const prompt = `I am an AI language model trained by OpenAI, based on the GPT-4 architecture. Please answer the following question: ${question}\n\nAnswer: `;

  const requestBody = {
    prompt: prompt,
    max_tokens: 100,
    n: 1,
    stop: "\n",
    temperature: 1.0,
    top_p: 1.0,
  };

  const config = {
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`,
    },
  };

  try {
    const response = await axios.post(apiUrl, requestBody, config);
    const answer = response.data.choices[0].text.trim();
    console.log(answer)
    
  } catch (error) {
    console.error(`Error: ${error}`);
    return null;
  }
}

// Usage example:
askChatGPT("what's 2 + 2")
  .then((answer) => console.log(`Answer: ${answer}`))
  .catch((error) => console.error(`Error: ${error}`));
