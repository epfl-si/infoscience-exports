{ pkgs, lib, config, inputs, ... }:

{
  # https://devenv.sh/basics/
  env = {

    DJANGO_SETTINGS_MODULE = "settings.dev";
    DJANGO_ENV = "dev";
    ALLOWED_HOSTS = "localhost";
    SERVER_HOST = "localhost";
    SITE_PATH = "/";
    SITE_URL = "http://localhost:3000";
    DEV_PORT = "3000";
    LOGGER_EXPORTS_FILE_PATH = "/tmp/infoscience_exports.log";
    LOGGER_MIGRATION_FILE_PATH = "/tmp/infoscience_exports_migrations.log";

    # Database
    DATABASE_HOST = "localhost";
    DATABASE_PORT = "5432";
    DATABASE_USER = "infoscience";
    DATABASE_PASSWORD = "infoscience";
    DB_NAME = "infoscience_exports";
    DATABASE_URL = "postgres://infoscience:infoscience@localhost:5432/infoscience_exports";

    # Needed by psql / pg_isready helpers
    PGPASSWORD = "infoscience";

    # Secrets
    SECRETSPEC_PROVIDER = "dotenv:/keybase/team/epfl_idevfsd/infoscience-exports/dev/secretspec.env";
    AUTH_ENTRA_TENANT_ID = config.secretspec.secrets.AUTH_ENTRA_TENANT_ID or "";
    AUTH_ENTRA_CLIENT_ID = config.secretspec.secrets.AUTH_ENTRA_CLIENT_ID or "";
    AUTH_ENTRA_SECRET = config.secretspec.secrets.AUTH_ENTRA_SECRET or "";
    SECRET_KEY = config.secretspec.secrets.SECRET_KEY or "";

    # Deploy
    SKIP_ANSIBLE_SUITECASE = "true";

  };

  # https://devenv.sh/packages/
  packages = with pkgs; [
    # PostgreSQL client tools (psql, pg_isready, pg_dump…)
    postgresql

    # Dev utilities
    gnumake
    git
    secretspec

    # Deploy utilities
    ansible
    ansible-lint
    openshift
  ];

  # https://devenv.sh/languages/
  languages.python = {
    enable  = true;
    version = "3.12";
    venv = {
      enable = true;
      requirements = ''
        kubernetes
      '';
    };
  };

  # https://devenv.sh/services/
  services.postgres = {
    enable      = true;
    package     = pkgs.postgresql;
    listen_addresses = "localhost";
    port        = 5432;

    initialDatabases = [{
      name = "infoscience_exports";
      user= "infoscience";
    }];

    settings = {
      log_connections = true;
    };
  };

  # https://devenv.sh/scripts/
  scripts = {

    # Bootstrap: install Python deps from Pipfile then migrate
    dev-setup.exec = ''
      set -e
      echo ">>> Installing Python dependencies via pipenv..."
      pip install pipenv --quiet
      pipenv install --dev --system
      echo ">>> Running Django migrations..."
      cd infoscience_exports
      python manage.py migrate
      python manage.py createcachetable
      echo ">>> Collecting static files..."
      python manage.py collectstatic --no-input
      echo ""
      echo ">>> Setup complete. Run 'dev-server' to start."
    '';

    # Start Django via gunicorn (mirrors docker-compose-dev.yml)
    dev-server.exec = ''
      cd infoscience_exports
      exec gunicorn \
        --max-requests 1 \
        --reload \
        -w 2 \
        -b :''${DEV_PORT} \
        wsgi:application
    '';

    # Handy alias for manage.py
    dj.exec = ''
      cd infoscience_exports
      exec python manage.py "$@"
    '';

    # Run the test suite
    dev-test.exec = ''
      cd infoscience_exports
      exec pytest "$@"
    '';

    set-first-user-as-admin.exec = ''
      cd infoscience_exports
      exec python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(id=1).update(is_staff=True, is_superuser=True)"
    '';
  };

  # https://devenv.sh/processes/
  processes = {
    django.exec = "dev-server";
  };

  # https://devenv.sh/enterShell/
  enterShell = ''
    # 🔐 Keybase check
    if [ -d "/keybase" ]; then
      if [ -r "/keybase" ]; then
        echo "🔐 /keybase is mounted and accessible ✅"
      else
        echo "⚠️  /keybase exists but is not readable"
      fi
    else
      echo "❌ /keybase is NOT mounted"
      echo "  👉 As we rely on Keybase for shared secrets,"
      echo "     make sure Keybase is running on your system."
    fi

    echo ""
    echo "Infoscience Exports dev environment"
    echo "====================================="
    echo "Notable tools: python, pg_*, ./ansible/exportsible"
    echo "Once dev processes are up and started,  access the DB on: $DATABASE_URL"
    echo ""
    echo "🆕  First time? Run Postgres and setup Django with:"
    echo "       devenv processes up -d; dev-setup"
    echo "    if you are the only user, get the admin rights with: set-first-user-as-admin"
    echo ""
    echo "▶️  Once setup done, next times, start directly with:"
    echo "       devenv processes up -d; dev-server"
    echo ""
    echo "⚙️  Django manage: dj <command>"
    echo ""
    echo "🧪  Tests: dev-test"
  '';
}
