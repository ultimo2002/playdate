document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector('form[action="/recommend"]');
    const gameInput = document.getElementById("game");
    const selectedGamesElement = document.getElementById("selected_games");
    const recommendButton = document.getElementById("recommend");
    const games = [];
    let renderedGameIds = new Set();  // Set to keep track of already rendered game IDs

    form.addEventListener("submit", handleFormSubmit);

    recommendButton.addEventListener("click", recommendGames);

    loadGames();

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

                gameInput.value = "";
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

    function createGameDiv(game, index, isNew) {
        const gameDiv = document.createElement("div");
        gameDiv.innerHTML = `ID: ${game.id}, Naam: ${game.name} `;

        const removeButton = document.createElement("a");
        removeButton.href = "#";
        removeButton.addEventListener("click", function(event) {
            event.preventDefault();
            animateAndRemove(gameDiv, index);
        });
        removeButton.classList.add("removeButton");

        gameDiv.appendChild(removeButton);
        selectedGamesElement.appendChild(gameDiv);

        if (isNew) {
            gameDiv.classList.add("pop-in"); // Add animation only for new games
        }
    }

    function renderGames() {
        // Clear the list before re-rendering
        selectedGamesElement.innerHTML = "";

        games.forEach((game, index) => {
            if (!renderedGameIds.has(game.id)) {
                renderedGameIds.add(game.id);  // Mark this game as rendered
                createGameDiv(game, index, true); // New game
            } else {
                createGameDiv(game, index, false); // Already rendered game
            }
        });
        const recommendGames = document.getElementById("recommend_games");
        recommendGames.classList.remove("pop-out");

        if (games.length > 0) {
            recommendGames.style.display = "initial";
            recommendGames.classList.add("pop-in");
        } else {
            recommendGames.classList.add("pop-out");
        }

        saveGames();
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

    function saveGames() {
        const gamesJson = JSON.stringify(games);
        const expireDate = new Date();
        expireDate.setHours(expireDate.getHours() + 6);
        document.cookie = `games=${gamesJson}; expires=${expireDate.toUTCString()}; path=/`;
    }

    function loadGames() {
        const cookie = document.cookie;
        const gameslist = cookie.match(/games=([^;]+)/);
        if (gameslist) {
            const gamesJson = gameslist[1];
            const loadedGames = JSON.parse(gamesJson);
            games.push(...loadedGames);
            renderGames();
        }
    }
    function recommendGames() {
        let gameIds = games.map(game => game.id).join(",");
        window.location.assign(`/recommend?games=${gameIds}`);
    }
});
