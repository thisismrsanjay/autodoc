




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
    
     <div onload="loadd" class="hovering-info-box" style=""fontFamily": "Lato",">
        <button class="close-button1">&times;</button>
        <div class="info-content">
        <h1>Response</h1>
        <h2 id="run-for-change-js">run-for-change.js</h2>
        <p>This script is used to detect changes in a git repository and execute a command if necessary. It is used in the <a href="https://github.com/vercel/next.js">Vercel/next.js</a> repository.</p>
        <h2 id="usage">Usage</h2>
        <p><code>node run-for-change.js --type &lt;change-type&gt; --exec &lt;command&gt;</code></p>
        <p>Where <code>&lt;change-type&gt;</code> is one of the following:</p>
        <ul>
        <li><code>docs</code></li>
        <li><code>deploy-examples</code></li>
        <li><code>cna</code></li>
        <li><code>next-codemod</code></li>
        <li><code>next-swc</code></li>
        </ul>
        <p>And <code>&lt;command&gt;</code> is the command to execute if changes are detected.</p>
        <p>The script also supports the <code>--not</code> and <code>--always-canary</code> flags.</p>
        <h2 id="overview">Overview</h2>
        <p>The script first checks the <code>GITHUB_EVENT_PATH</code> environment variable or the <code>GITHUB_REF_NAME</code> and <code>GITHUB_REPOSITORY</code> environment variables to determine the branch name and remote URL. </p>
        <p>It then fetches the <code>origin/canary</code> branch and uses <code>git diff</code> to detect changes.</p>
        <p>It then checks the list of change items associated with the given change type to determine if any of the changed files match. If so, it executes the given command.</p>
        <p>If the <code>--listChangedDirectories</code> flag is provided, the script will output a list of changed directories instead of executing the command.
        Preview
        run-for-change.js
        This script is used to detect changes in a git repository and execute a command if necessary. It is used in the Vercel/next.js repository.</p>
        <p>Usage
        node run-for-change.js --type <change-type> --exec <command></p>
        <p>Where <change-type> is one of the following:</p>
        <p>docs
        deploy-examples
        cna
        next-codemod
        next-swc
        And <command> is the command to execute if changes are detected.</p>
        <p>The script also supports the --not and --always-canary flags.</p>
        <p>Overview
        The script first checks the GITHUB_EVENT_PATH environment variable or the GITHUB_REF_NAME and GITHUB_REPOSITORY environment variables to determine the branch name and remote URL.</p>
        <p>It then fetches the origin/canary branch and uses git diff to detect changes.</p>
        <p>It then checks the list of change items associated with the given change type to determine if any of the changed files match. If so, it executes the given command.</p>
        <p>If the --listChangedDirectories flag is provided, the script will output a list of changed directories instead of executing the command.</p>
        
        </div>
      </div>

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


