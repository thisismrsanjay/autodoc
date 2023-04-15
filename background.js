
chrome.runtime.onInstalled.addListener(function() {
    console.log("install")
    chrome.contextMenus.create({
        "id":"test",
        "title":"Generate Documentation",
        "contexts":["selection"]
    })
   })
//get selected message  ✅
//send to api 
//make waiting animation 
//get the result 
// send back to content.js


let createDoc = (info,tab)=>{
    let msg = {
        type:'createDoc',
        body: info.selectionText
    }

    

    function OpenaiFetchAPI() {
        console.log("Calling GPT3")
        var url = "https://api.openai.com/v1/engines/davinci/completions";
        var bearer = 'Bearer ' + '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';
        fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': bearer,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "prompt": "2+2 is ? ",
            })
    
    
        }).then(response => {
            return response.json()
           
        }).then(data=>{
            console.log(data)
            console.log("REPLY:",data['choices'][0].text)
            
        })
            .catch(error => {
                console.log('Something bad happened ' + error)
            });
    
    }
    OpenaiFetchAPI();
    chrome.tabs.sendMessage(tab.id,msg,()=>{
        console.log("message sent")
    })
    console.log(tab);
    
}

chrome.contextMenus.onClicked.addListener(
    (info,tab)=>{
        createDoc(info,tab)
    }
  )
// contexts should be selection s


