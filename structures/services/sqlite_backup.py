import hashlib
import json
import os
import re
import shutil
import sqlite3
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

BACKUP_NAME_RE = re.compile(r"^bdd-pe-[a-z0-9-]+-\d{8}T\d{6}\d{6}Z\.sqlite3$")
BACKUP_TIMESTAMP_RE = re.compile(
    r"^bdd-pe-[a-z0-9-]+-(\d{8}T\d{6}\d{6}Z)\.sqlite3$"
)
LOCK_NAME = ".bddpe-backup.lock"
CATALOG_NAME = ".bddpe-backups.json"
STALE_LOCK_AFTER = timedelta(minutes=30)
MIN_FREE_SPACE = 50 * 1024 * 1024


class SQLiteBackupError(RuntimeError):
    """Échec de création ou de vérification d'une sauvegarde SQLite."""


@dataclass(frozen=True, slots=True)
class BackupResult:
    path: Path
    sha256: str
    size: int


@dataclass(frozen=True, slots=True)
class BackupInfo:
    name: str
    size: int
    created: datetime | None
    verified: bool
    sha256: str | None


def is_backup_name(name: str) -> bool:
    return bool(BACKUP_NAME_RE.fullmatch(name))


def verify_sqlite_database(path: Path) -> None:
    if not path.is_file():
        raise SQLiteBackupError(f"Fichier SQLite introuvable : {path}.")
    try:
        with closing(
            sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
        ) as connection:
            result = connection.execute("PRAGMA integrity_check").fetchone()
    except sqlite3.Error as error:
        raise SQLiteBackupError(f"Impossible de lire la sauvegarde SQLite : {path}.") from error
    if result != ("ok",):
        raise SQLiteBackupError(f"Le contrôle d'intégrité SQLite a échoué : {result!r}.")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as backup_file:
        while chunk := backup_file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def create_sqlite_backup(
    source: Path,
    destination_directory: Path,
    *,
    environment: str = "production",
) -> BackupResult:
    if not source.is_file():
        raise SQLiteBackupError(f"La base SQLite est introuvable : {source}.")
    source = source.resolve(strict=True)
    destination_directory = destination_directory.resolve()
    if destination_directory == source.parent:
        raise SQLiteBackupError("Le répertoire de sauvegarde doit être distinct de celui de la base.")

    destination_directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    destination = destination_directory / f"bdd-pe-{environment}-{timestamp}.sqlite3"
    temporary = destination.with_suffix(".sqlite3.partial")

    try:
        with closing(sqlite3.connect(source)) as source_connection:
            with closing(sqlite3.connect(temporary)) as backup_connection:
                source_connection.backup(backup_connection)
        verify_sqlite_database(temporary)
        temporary.replace(destination)
    except (OSError, sqlite3.Error, SQLiteBackupError) as error:
        if temporary.exists():
            temporary.unlink()
        if isinstance(error, SQLiteBackupError):
            raise
        raise SQLiteBackupError("La sauvegarde SQLite n'a pas pu être créée.") from error

    return BackupResult(
        path=destination,
        sha256=_sha256(destination),
        size=destination.stat().st_size,
    )


def _parse_backup_timestamp(name: str) -> datetime | None:
    match = BACKUP_TIMESTAMP_RE.match(name)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%Y%m%dT%H%M%S%fZ").replace(tzinfo=UTC)
    except ValueError:
        return None


def _catalog_path(directory: Path) -> Path:
    return directory / CATALOG_NAME


def _read_catalog(directory: Path) -> dict:
    try:
        data = json.loads(_catalog_path(directory).read_text("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_catalog(directory: Path, catalog: dict) -> None:
    path = _catalog_path(directory)
    temporary = path.with_suffix(".json.tmp")
    try:
        temporary.write_text(json.dumps(catalog, sort_keys=True), "utf-8")
        temporary.replace(path)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def _resolve_backup_path(directory: Path, name: str) -> Path:
    if not is_backup_name(name):
        raise SQLiteBackupError("Nom de sauvegarde invalide.")
    path = (directory / name).resolve()
    if path.parent != directory:
        raise SQLiteBackupError("Nom de sauvegarde invalide.")
    if not path.is_file() or path.is_symlink():
        raise SQLiteBackupError("Fichier de sauvegarde introuvable.")
    return path


def list_sqlite_backups(directory: Path) -> list[BackupInfo]:
    directory = directory.resolve()
    if not directory.is_dir():
        return []
    catalog = _read_catalog(directory)
    backups = []
    for path in directory.glob("bdd-pe-*.sqlite3"):
        if not is_backup_name(path.name) or not path.is_file() or path.is_symlink():
            continue
        entry = catalog.get(path.name, {})
        backups.append(
            BackupInfo(
                name=path.name,
                size=path.stat().st_size,
                created=_parse_backup_timestamp(path.name),
                verified=bool(entry.get("verified")),
                sha256=entry.get("sha256"),
            )
        )
    backups.sort(key=lambda backup: backup.created or datetime.min.replace(tzinfo=UTC), reverse=True)
    return backups


def mark_backup_verified(directory: Path, name: str) -> tuple[str, int]:
    directory = directory.resolve()
    path = _resolve_backup_path(directory, name)
    verify_sqlite_database(path)
    sha256 = _sha256(path)
    size = path.stat().st_size
    catalog = _read_catalog(directory)
    catalog[name] = {"verified": True, "sha256": sha256}
    try:
        _write_catalog(directory, catalog)
    except OSError as error:
        raise SQLiteBackupError("Impossible de mettre à jour l'état de la sauvegarde.") from error
    return sha256, size


def delete_sqlite_backup(directory: Path, name: str) -> None:
    directory = directory.resolve()
    path = _resolve_backup_path(directory, name)
    try:
        path.unlink()
    except OSError as error:
        raise SQLiteBackupError("Impossible de supprimer la sauvegarde.") from error
    catalog = _read_catalog(directory)
    catalog.pop(name, None)
    try:
        _write_catalog(directory, catalog)
    except OSError as error:
        raise SQLiteBackupError("Impossible de mettre à jour l'état de la sauvegarde.") from error


def purge_sqlite_backups(directory: Path, keep: int) -> int:
    directory = directory.resolve()
    if keep < 1:
        raise SQLiteBackupError("La rétention doit être au moins égale à 1.")
    removed = 0
    for backup in list_sqlite_backups(directory)[keep:]:
        delete_sqlite_backup(directory, backup.name)
        removed += 1
    return removed


@contextmanager
def backup_lock(directory: Path):
    lock_path = directory / LOCK_NAME
    while True:
        try:
            file_descriptor = os.open(
                lock_path,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            )
        except FileExistsError:
            try:
                lock_age = datetime.now().timestamp() - lock_path.stat().st_mtime
            except OSError:
                raise SQLiteBackupError("Une sauvegarde est déjà en cours.") from None
            if lock_age > STALE_LOCK_AFTER.total_seconds():
                lock_path.unlink(missing_ok=True)
                continue
            raise SQLiteBackupError("Une sauvegarde est déjà en cours.")
        except OSError:
            raise SQLiteBackupError("Impossible de verrouiller la sauvegarde.") from None
        break
    try:
        with os.fdopen(file_descriptor, "w") as lock_file:
            lock_file.write(str(os.getpid()))
        yield
    finally:
        lock_path.unlink(missing_ok=True)


def _ensure_disk_space(directory: Path, source: Path) -> None:
    required = max(source.stat().st_size * 2, MIN_FREE_SPACE)
    try:
        free = shutil.disk_usage(directory).free
    except OSError as error:
        raise SQLiteBackupError("Impossible de vérifier l'espace disque.") from error
    if free < required:
        raise SQLiteBackupError(
            "Espace disque insuffisant pour la sauvegarde "
            f"({required // (1024 * 1024)} Mo requis)."
        )


def run_backup(
    source: Path,
    directory: Path,
    *,
    keep: int,
    environment: str = "production",
) -> BackupResult:
    directory = Path(directory)
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise SQLiteBackupError("Le répertoire de sauvegarde est inaccessible.") from error
    _ensure_disk_space(directory, source)
    with backup_lock(directory):
        result = create_sqlite_backup(source, directory, environment=environment)
        catalog = _read_catalog(directory)
        catalog[result.path.name] = {"verified": True, "sha256": result.sha256}
        try:
            _write_catalog(directory, catalog)
        except OSError as error:
            raise SQLiteBackupError("Impossible d'enregistrer l'état de la sauvegarde.") from error
        purge_sqlite_backups(directory, keep)
        return result
