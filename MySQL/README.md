# MySQL configuration

Client defaults for connecting to the database server when running scripts from [`../Schemas/`](../Schemas/).

## `my.cnf`

Sample `[client]` section:

```ini
[client]
user     = username
password = password
```

Optional settings (commented in the file):

- `port = 3306`
- `validate-password = off`

## Installation

Copy or merge into the system config path your MySQL install expects, for example:

```bash
# Linux — path may vary by distribution
sudo cp my.cnf /etc/mysql/my.cnf

# macOS (Homebrew) — often user-level
mkdir -p ~/.my.cnf.d
cp my.cnf ~/.my.cnf
```

Adjust `user` and `password` to match a account that can run the schema scripts. For grant examples, you typically need a privileged user (e.g. `root`).

## Usage

With a client config in place, CLI tools pick up credentials automatically:

```bash
mysql < ../Schemas/Animal.sql
```

Or connect explicitly:

```bash
mysql -u root -p
```

Then run SQL from [`../Schemas/GrantPermissions.sql`](../Schemas/GrantPermissions.sql) to create application users. Model those grants with `Access` in [`../database/access.py`](../database/access.py).

## Security

- Do not commit real passwords to version control.
- Prefer environment variables or a local, gitignored config for production credentials.
- Grant least privilege (`SELECT` only, specific tables) instead of `ALL` when possible.
