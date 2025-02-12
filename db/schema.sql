CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS addresses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ip TEXT NOT NULL,
  user_id INTEGER,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS characters (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  name TEXT NOT NULL,
  class TEXT NOT NULL CHECK(class IN ('Wizard', 'Warlock', 'Sorcerer', 'Rogue','Ranger', 'Paladin', 'Monk', 'Fighter', 'Druid', 'Cleric', 'Bard', 'Barbarian')),
  gender TEXT NOT NULL CHECK(gender IN ('Male', 'Female','Trans Female to male','Trans male to female','Non-binary','other')),
  race TEXT NOT NULL CHECK(race in ('Dwarf','Elf','Halfling','Human','Dragonborn','Gnome','Goliath','Orc','Tiefling', 'Centaur', 'Fairy', 'Goblin')),
  strength INTEGER NOT NULL,
  dexterity INTEGER NOT NULL,
  constitution INTEGER NOT NULL,
  intelligence INTEGER NOT NULL,
  wisdom INTEGER NOT NULL,
  charisma INTEGER NOT NULL,
  x INTEGER NOT NULL,
  y INTEGER NOT NULL,
  xp INTEGER NOT NULL,
  lvl INTEGER NOT NULL,
  max_weight INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS inventory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  character_id INTEGER,
  item_id INTEGER,
  quantity INTEGER DEFAULT 1,
  FOREIGN KEY (character_id) REFERENCES characters(id),
  FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  weight REAL DEFAULT 0.0,
  rarity TEXT DEFAULT 'common',
  itemtype TEXT NOT NULL CHECK(itemtype IN ('Weapon','Material','Potion','Food')),
  weapondamage REAL DEFAULT 0.0,
  weaponblock REAL DEFAULT 0.0,
  weaponhands INTEGER DEFAULT 0,
  worth REAL DEFAULT 1.0,
  potioneffectid INTEGER,
  foodspoilage REAl DEFAULT 100.0,
  foodworth REAL DEFAULT 10.0,
  foodsickness REAL DEFAULT 0.0,
  foodeffectid INTEGER,
  FOREIGN KEY (foodeffectid) REFERENCES effects(id),
  FOREIGN KEY (potioneffectid) REFERENCES effects(id)
);

CREATE TABLE IF NOT EXISTS effects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  character_id INTEGER,
  timer INTEGER DEFAULT 60.0,
  FOREIGN KEY (character_id) REFERENCES characters(id)
);
