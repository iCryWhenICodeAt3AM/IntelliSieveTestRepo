// job card click effect
$('.card').click(function () {
    $(this).toggleClass('clicked');
});

// stats card value change animation

// Select all the counter elements
const counters = document.querySelectorAll(".counter");

// Define the animation function
function animateValue(counter, targetValue) {
    // Set the starting value to zero
    let currentValue = 0;

    function tick() {
        if (currentValue < targetValue) {
            // Increment the current value
            currentValue += 5;

            // Update the counter element's text content
            counter.textContent = currentValue;

            // Request the next animation frame
            requestAnimationFrame(tick);
        }
    }

    // Start the animation
    tick();
}

// Loop through all the counter elements and apply the animation
counters.forEach(counter => {
    const targetValue = parseInt(counter.dataset.target);
    animateValue(counter, targetValue);
});
//for linking of jobpost
function redirectToJobpost(id) {
            window.location.href = "/jobpost";
        }