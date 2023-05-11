




let receiver = (message,sender,sendResponse)=>{
    console.log("received message",message)
    init();
    sendResponse({received:"message recieved"})
}



chrome.runtime.onMessage.addListener(receiver)




//injector inject after receving message 
const init = function(){
    const injectElement =  document.createElement('div');
    injectElement.className = 'autodoc';
    injectElement.innerHTML=`
    

`
    document.body.appendChild(injectElement)


    const closeButton = document.querySelector('.close-button1');
    const hoveringInfoBox = document.querySelector('.hovering-info-box');
    let isMouseDown = false;
    let offsetX, offsetY;

    closeButton.addEventListener('click', function () {
        hoveringInfoBox.style.display = 'none';
    });

    hoveringInfoBox.addEventListener('mousedown', function (event) {
        isMouseDown = true;
        offsetX = event.clientX - hoveringInfoBox.offsetLeft;
        offsetY = event.clientY - hoveringInfoBox.offsetTop;
    });

    window.addEventListener('mousemove', function (event) {
        if (isMouseDown) {
            const x = event.clientX - offsetX;
            const y = event.clientY - offsetY;
            hoveringInfoBox.style.left = x + 'px';
            hoveringInfoBox.style.top = y + 'px';
        }
    });

    window.addEventListener('mouseup', function () {
        isMouseDown = false;
    });
    
}


