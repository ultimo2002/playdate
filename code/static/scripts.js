document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector('form[action="/recommend"]');
    const gameInput = document.getElementById("game");
    const selectedGamesElement = document.getElementById("selected_games");
    const games = [];

    form.addEventListener("submit", handleFormSubmit);

    function handleFormSubmit(event) {
        event.preventDefault();

        const gameName = gameInput.value.trim();
        if (!gameName) {
            alert("Enter a game name");
            return;
        }

        fetchGameData(gameName)
            .then(data => {
                if (!data) {
                    alert("The game you entered does not exist");
                    return;
                }
                else if (isGameAlreadyInList(data)) {
                    alert("You already selected this game");
                    return;
                }

                games.push(data);
                renderGames();
            })
            .catch(handleError);
    }

    function fetchGameData(gameName) {
        return fetch(`app/similar/${encodeURIComponent(gameName)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error, status = ${response.status}`);
                }
                return response.json();
            });
    }

    function isGameAlreadyInList(game) {
        return games.some(existingGame => existingGame.id === game.id);
    }

    let renderedGameIds = new Set();  // Set to keep track of already rendered game IDs

    function renderGames() {
        const recommendGames = document.getElementById("recommend_games");
        recommendGames.style.display = "initial";

        // Render the selected games list
        selectedGamesElement.innerHTML = ""; // Clear the list before re-rendering

        games.forEach((game, index) => {
            if (!renderedGameIds.has(game.id)) {
                // Only add the pop-in class for new games (that haven't been rendered yet)
                renderedGameIds.add(game.id);  // Mark this game as rendered

                const gameDiv = document.createElement("div");
                gameDiv.innerHTML = `ID: ${game.id}, Naam: ${game.name} `;

                const removeButton = document.createElement("a");
                removeButton.href = "#";
                removeButton.addEventListener("click", function(event) {
                    event.preventDefault(); // Stops `<a>` from navigating
                    animateAndRemove(gameDiv, index);
                });
                removeButton.classList.add("removeButton");

                gameDiv.appendChild(removeButton);
                selectedGamesElement.appendChild(gameDiv);

                // Add the pop-in class to trigger the animation
                gameDiv.classList.add("pop-in");
            } else {
                // Handle already rendered games (just render without animation)
                const existingGameDiv = document.createElement("div");
                existingGameDiv.innerHTML = `ID: ${game.id}, Naam: ${game.name} `;
                const removeButton = document.createElement("a");
                removeButton.href = "#";
                removeButton.addEventListener("click", function(event) {
                    event.preventDefault();
                    animateAndRemove(existingGameDiv, index);
                });
                removeButton.classList.add("removeButton");

                existingGameDiv.appendChild(removeButton);
                selectedGamesElement.appendChild(existingGameDiv);
            }
        });
    }


    function animateAndRemove(gameDiv, index) {
        gameDiv.classList.add("pop-out"); // Apply animation
        gameDiv.addEventListener("animationend", () => {
            removeGame(index);
        });
    }

    function removeGame(index) {
        games.splice(index, 1);
        renderGames();
    }

    function handleError(error) {
        console.error("Error: ", error);
        alert("Error: " + error);
    }
});
