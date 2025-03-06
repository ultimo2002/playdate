document.addEventListener("DOMContentLoaded", function() {
    // Whe have multiple "card" classes, with id "appid-{number}". And there are divs that are hidden with id: recommended-for-{gamename}
    const cards = document.querySelectorAll(".selected-card");
    cards.forEach(card => {
        var name = card.querySelector(".game-title").innerHTML.toLowerCase().replace(/ /g, "-");
        name = name.replace(/[^a-zA-Z0-9 ]/g, "");
        console.log(name);
        const recommendedFor = document.getElementById(`recommended-for-${name}`);

        card.addEventListener("click", function() {
            card.classList.toggle("folded");
            if (recommendedFor.style.display === "none") {
                recommendedFor.style.display = "block";
            } else {
                recommendedFor.style.display = "none";
            }
        });
    });
});