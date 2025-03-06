from sqlite3 import IntegrityError

from src.database.models import *
def fill_database(db):
    entries = [
        # Categories
        Category(id=1, name="Games"),
        Category(id=2, name="Productivity"),
        Category(id=3, name="Education"),
        Category(id=4, name="Health & Fitness"),
        Category(id=5, name="Entertainment"),

        # Genres
        Genre(id=1, name="Action"),
        Genre(id=2, name="Strategy"),
        Genre(id=3, name="Simulation"),
        Genre(id=4, name="RPG"),
        Genre(id=5, name="Puzzle"),

        # Tags
        Tags(id=1, name="Multiplayer"),
        Tags(id=2, name="Single-Player"),
        Tags(id=3, name="Online"),
        Tags(id=4, name="Offline"),
        Tags(id=5, name="Casual"),

        # Apps (1-15)
        App(
            id=1,
            name="Space Adventure Game",
            short_description="Explore the galaxy in this exciting action-packed game!",
            price="Free",
            developer="Game Studio X",
            header_image="http://example.com/header1.jpg",
            background_image="http://example.com/bg1.jpg"
        ),
        App(
            id=2,
            name="Task Master Pro",
            short_description="Boost your productivity with advanced task management.",
            price="$9.99",
            developer="Productivity Inc",
            header_image="http://example.com/header2.jpg",
            background_image="http://example.com/bg2.jpg"
        ),
        App(
            id=3,
            name="Learn Python Interactive",
            short_description="Interactive lessons to master Python programming.",
            price="Free",
            developer="EduTech Solutions",
            header_image="http://example.com/header3.jpg",
            background_image="http://example.com/bg3.jpg"
        ),
        App(
            id=4,
            name="Fitness Tracker Plus",
            short_description="Track your workouts and stay healthy with guided plans.",
            price="$4.99",
            developer="Health & Wellness Co",
            header_image="http://example.com/header4.jpg",
            background_image="http://example.com/bg4.jpg"
        ),
        App(
            id=5,
            name="Movie Streamer",
            short_description="Stream thousands of movies and TV shows instantly.",
            price="$14.99",
            developer="Entertainment Hub",
            header_image="http://example.com/header5.jpg",
            background_image="http://example.com/bg5.jpg"
        ),
        App(
            id=6,
            name="Puzzle Quest",
            short_description="Solve challenging puzzles in this addictive game.",
            price="Free",
            developer="Brainy Games Studio",
            header_image="http://example.com/header6.jpg",
            background_image="http://example.com/bg6.jpg"
        ),
        App(
            id=7,
            name="Daily Planner",
            short_description="Organize your day with smart scheduling and reminders.",
            price="$2.99",
            developer="Productivity Tools Ltd",
            header_image="http://example.com/header7.jpg",
            background_image="http://example.com/bg7.jpg"
        ),
        App(
            id=8,
            name="Math Tutor AI",
            short_description="AI-powered math learning for all levels.",
            price="$7.99",
            developer="EduTech Innovations",
            header_image="http://example.com/header8.jpg",
            background_image="http://example.com/bg8.jpg"
        ),
        App(
            id=9,
            name="Yoga & Meditation",
            short_description="Daily yoga routines and meditation guides.",
            price="Free",
            developer="Mind & Body Wellness",
            header_image="http://example.com/header9.jpg",
            background_image="http://example.com/bg9.jpg"
        ),
        App(
            id=10,
            name="Music Studio Pro",
            short_description="Create and mix music like a professional.",
            price="$19.99",
            developer="Audio Creators Inc",
            header_image="http://example.com/header10.jpg",
            background_image="http://example.com/bg10.jpg"
        ),
        App(
            id=11,
            name="Racing Champions",
            short_description="High-speed racing with realistic physics.",
            price="$12.99",
            developer="Speed Demons Studio",
            header_image="http://example.com/header11.jpg",
            background_image="http://example.com/bg11.jpg"
        ),
        App(
            id=12,
            name="Expense Manager",
            short_description="Track and manage your finances effortlessly.",
            price="Free",
            developer="Finance Tools Corp",
            header_image="http://example.com/header12.jpg",
            background_image="http://example.com/bg12.jpg"
        ),
        App(
            id=13,
            name="History Explorer",
            short_description="Interactive journeys through world history.",
            price="$5.99",
            developer="EduLearn Systems",
            header_image="http://example.com/header13.jpg",
            background_image="http://example.com/bg13.jpg"
        ),
        App(
            id=14,
            name="Cooking Assistant",
            short_description="Step-by-step recipes and meal planning.",
            price="$8.99",
            developer="Culinary Experts LLC",
            header_image="http://example.com/header14.jpg",
            background_image="http://example.com/bg14.jpg"
        ),
        App(
            id=15,
            name="Photo Editor Deluxe",
            short_description="Professional photo editing tools and filters.",
            price="Free",
            developer="Creative Software Co",
            header_image="http://example.com/header15.jpg",
            background_image="http://example.com/bg15.jpg"
        ),
        # AppCategory relationships (15)
        AppCategory(app_id=1, category_id=1),  # Space Adventure Game -> Games
        AppCategory(app_id=2, category_id=2),  # Task Master Pro -> Productivity
        AppCategory(app_id=3, category_id=3),  # Learn Python Interactive -> Education
        AppCategory(app_id=4, category_id=4),  # Fitness Tracker Plus -> Health & Fitness
        AppCategory(app_id=5, category_id=5),  # Movie Streamer -> Entertainment
        AppCategory(app_id=6, category_id=1),  # Puzzle Quest -> Games
        AppCategory(app_id=7, category_id=2),  # Daily Planner -> Productivity
        AppCategory(app_id=8, category_id=3),  # Math Tutor AI -> Education
        AppCategory(app_id=9, category_id=4),  # Yoga & Meditation -> Health & Fitness
        AppCategory(app_id=10, category_id=5),  # Music Studio Pro -> Entertainment
        AppCategory(app_id=11, category_id=1),  # Racing Champions -> Games
        AppCategory(app_id=12, category_id=2),  # Expense Manager -> Productivity
        AppCategory(app_id=13, category_id=3),  # History Explorer -> Education
        AppCategory(app_id=14, category_id=4),  # Cooking Assistant -> Health & Fitness
        AppCategory(app_id=15, category_id=5),  # Photo Editor Deluxe -> Entertainment

        # AppGenre relationships (15)
        AppGenre(app_id=1, genre_id=1),  # Space Adventure Game -> Action
        AppGenre(app_id=2, genre_id=2),  # Task Master Pro -> Strategy
        AppGenre(app_id=3, genre_id=3),  # Learn Python Interactive -> Simulation
        AppGenre(app_id=4, genre_id=4),  # Fitness Tracker Plus -> RPG
        AppGenre(app_id=5, genre_id=5),  # Movie Streamer -> Puzzle
        AppGenre(app_id=6, genre_id=1),  # Puzzle Quest -> Action
        AppGenre(app_id=7, genre_id=2),  # Daily Planner -> Strategy
        AppGenre(app_id=8, genre_id=3),  # Math Tutor AI -> Simulation
        AppGenre(app_id=9, genre_id=4),  # Yoga & Meditation -> RPG
        AppGenre(app_id=10, genre_id=5),  # Music Studio Pro -> Puzzle
        AppGenre(app_id=11, genre_id=1),  # Racing Champions -> Action
        AppGenre(app_id=12, genre_id=2),  # Expense Manager -> Strategy
        AppGenre(app_id=13, genre_id=3),  # History Explorer -> Simulation
        AppGenre(app_id=14, genre_id=4),  # Cooking Assistant -> RPG
        AppGenre(app_id=15, genre_id=5),  # Photo Editor Deluxe -> Puzzle

        # AppTags relationships (15)
        AppTags(app_id=1, tag_id=1),  # Space Adventure Game -> Multiplayer
        AppTags(app_id=2, tag_id=2),  # Task Master Pro -> Single-Player
        AppTags(app_id=3, tag_id=3),  # Learn Python Interactive -> Online
        AppTags(app_id=4, tag_id=4),  # Fitness Tracker Plus -> Offline
        AppTags(app_id=5, tag_id=5),  # Movie Streamer -> Casual
        AppTags(app_id=6, tag_id=1),  # Puzzle Quest -> Multiplayer
        AppTags(app_id=7, tag_id=2),  # Daily Planner -> Single-Player
        AppTags(app_id=8, tag_id=3),  # Math Tutor AI -> Online
        AppTags(app_id=9, tag_id=4),  # Yoga & Meditation -> Offline
        AppTags(app_id=10, tag_id=5),  # Music Studio Pro -> Casual
        AppTags(app_id=11, tag_id=1),  # Racing Champions -> Multiplayer
        AppTags(app_id=12, tag_id=2),  # Expense Manager -> Single-Player
        AppTags(app_id=13, tag_id=3),  # History Explorer -> Online
        AppTags(app_id=14, tag_id=4),  # Cooking Assistant -> Offline
        AppTags(app_id=15, tag_id=5),  # Photo Editor Deluxe -> Casual
    ]

    # Add apps to the session and commit
    try:
        db.add_all(entries)
    except IntegrityError:
        pass
    db.commit()


