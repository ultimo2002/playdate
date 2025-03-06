document.addEventListener("DOMContentLoaded", function() {
    // Whe have multiple "card" classes, with id "appid-{number}". And there are divs that are hidden with id: recommended-for-{gamename}
    const cards = document.querySelectorAll(".selected-card");
    const closeAllButton = document.getElementById("closeall");
    cards.forEach(card => {
        var name = card.querySelector(".game-title").innerHTML.toLowerCase().replace(/ /g, "-");
        name = name.replace(/[^a-zA-Z0-9 ]/g, "");
        const recommendedFor = document.getElementById(`recommended-for-${name}`);

        card.addEventListener("click", function() {
            card.classList.toggle("folded");
            if (recommendedFor.style.display === "none") {
                recommendedFor.style.display = "block";
            } else {
                recommendedFor.style.display = "none";
            }
        });

        closeAllButton.addEventListener("click", function() {
            if (closeAllButton.innerHTML === "Close all") {
                card.classList.add("folded");
                recommendedFor.style.display = "none";
            } else {
                card.classList.remove("folded");
                recommendedFor.style.display = "block";
            }
        });
    });

    // toogle close all button with open all button replace text
    closeAllButton.addEventListener("click", function() {
        if (closeAllButton.innerHTML === "Close all") {
            closeAllButton.innerHTML = "Open all";
        } else {
            closeAllButton.innerHTML = "Close all";
        }
    });
});