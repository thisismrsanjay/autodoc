window.addEventListener('DOMContentLoaded', function () {
    const closeButton = document.querySelector('.close-button');
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
});
