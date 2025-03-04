document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector('form[action="/recommend"]');
    const gameInput1 = document.getElementById("game1");
    const gameInput2 = document.getElementById("game2");
    const gameInput3 = document.getElementById("game3");
    const selectedGamesElement = document.getElementById("selected_games");
    const recommendButton = document.getElementById("recommend");
    const games = [];
    let renderedGameIds = new Set();  // Set to keep track of already rendered game IDs

    form.addEventListener("submit", handleFormSubmit);

    recommendButton.addEventListener("click", recommendGames);

    loadGames();

    function handleFormSubmit(event) {
        event.preventDefault();

        const gameName1 = gameInput1.value.trim();
        const gameName2 = gameInput2.value.trim();
        const gameName3 = gameInput3.value.trim();

        // Collect all non-empty game inputs
        const gameNames = [gameName1, gameName2, gameName3].filter(name => name);

        if (gameNames.length === 0) {
            alert("Enter at least one game name");
            return;
        }

        // Fetch data for each non-empty game name
        gameNames.forEach(gameName => {
            fetchGameData(gameName)
                .then(data => {
                    if (!data) {
                        alert(`The game "${gameName}" does not exist`);
                        return;
                    } else if (isGameAlreadyInList(data)) {
                        alert(`You already selected the game "${gameName}"`);
                        return;
                    }

                    games.push(data);
                    renderGames();
                })
                .catch(handleError);
        });

        // Clear input fields after submission
        gameInput1.value = "";
        gameInput2.value = "";
        gameInput3.value = "";
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
