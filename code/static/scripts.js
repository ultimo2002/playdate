document.addEventListener("DOMContentLoaded", function() {
    document.querySelector('form[action="/recommend"]').addEventListener("submit", function(event) {
        event.preventDefault();

        let gameName = document.getElementById("game").value.trim();
        if (gameName === "") {
            alert("Enter a game name");
            return;
        }

        let url = `app/similar/${encodeURIComponent(gameName)}`;

        let selected_games_element = document.getElementById("selected_games");

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error("HTTP error, status = " + response.status);
                }
                return response.json();
            })
            .then(data => {
                console.log(data);
                if (data.length === 0) {
                    alert("The game you entered does not exist");
                    return;
                }

                // When the game is already in the list, don't add it again
                let existing_divs = selected_games_element.querySelectorAll("div");
                for (let div of existing_divs) {
                    if (div.innerHTML.includes(data.name)) {
                        console.log("Game already in list");
                        return;
                    }
                }

                let new_div = document.createElement("div");
                new_div.innerHTML = `ID: ${data.id}, Naam: ${data.name}`;
                selected_games_element.appendChild(new_div);
            })
            .catch(error => {
                console.error("Error: ", error);
                alert("Error: " + error);
            });
    });
});