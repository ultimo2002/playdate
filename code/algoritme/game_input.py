def find_similar_games(game_name, game_database):
    if game_name not in game_database:
        return f"The game '{game_name}' has not been found in our database."

    target_genres = game_database[game_name]
    similarity_scores = []  # Lijst om overeenkomsten op te slaan

    # Stap 2: Vergelijk met alle andere games
    for other_game, genres in game_database.items():
        if other_game == game_name:
            continue

        common_genres = target_genres & genres
        if len(common_genres) > 0:
            similarity_scores.append((other_game, len(common_genres), common_genres))

    # Stap 3: Sorteer op meest overeenkomende genres
    similarity_scores.sort(key=lambda x: x[1], reverse=True)

    return similarity_scores

game_db = {
    "Elden Ring": {"RPG", "Open World", "Action", "Fantasy", "Soulslike"},
    "The Witcher 3": {"RPG", "Open World", "Story-driven", "Fantasy", "Action"},
    "Dark Souls 3": {"RPG", "Action", "Difficult", "Fantasy", "Soulslike"},
    "Cyberpunk 2077": {"RPG", "Open World", "FPS", "Sci-Fi", "Story-driven"},
    "GTA V": {"Open World", "Action", "Crime", "Story-driven", "Multiplayer"},
    "Red Dead Redemption 2": {"Open World", "Story-driven", "Western", "Action"},
    "Skyrim": {"RPG", "Open World", "Fantasy", "Story-driven", "Action"},
    "Bloodborne": {"RPG", "Action", "Difficult", "Soulslike", "Horror"},
    "Horizon Zero Dawn": {"Open World", "Action", "RPG", "Sci-Fi", "Story-driven"},
    "God of War": {"Action", "Story-driven", "Fantasy", "Adventure"},
    "Assassin's Creed Valhalla": {"Open World", "Action", "RPG", "Historical"},
    "Far Cry 6": {"Open World", "FPS", "Action", "Shooter"},
    "Doom Eternal": {"FPS", "Action", "Shooter", "Fast-paced"},
    "Call of Duty: Modern Warfare": {"FPS", "Shooter", "Multiplayer", "Action"},
    "Battlefield 2042": {"FPS", "Multiplayer", "Shooter", "Action"},
    "The Legend of Zelda: Breath of the Wild": {"Open World", "Adventure", "Fantasy", "Puzzle"},
    "Hollow Knight": {"Metroidvania", "Indie", "Action", "Difficult"},
    "Celeste": {"Platformer", "Indie", "Difficult", "Story-driven"},
    "Stardew Valley": {"Indie", "Farming", "Relaxing", "Simulation"},
    "Terraria": {"Sandbox", "Survival", "Adventure", "Indie"},
    "Minecraft": {"Sandbox", "Survival", "Adventure", "Multiplayer"},
    "Baldur's Gate 3": {"RPG", "Turn-Based", "Fantasy", "Story-driven"},
    "Divinity: Original Sin 2": {"RPG", "Turn-Based", "Fantasy", "Story-driven"},
}

game_name = input("Input a game name: ")
result = find_similar_games(game_name, game_db)

for game, match_count, genres in result:
    print(f"{game} - Similarity: {match_count} genres ({', '.join(genres)})")
