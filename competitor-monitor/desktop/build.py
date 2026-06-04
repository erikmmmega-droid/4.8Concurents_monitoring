"""
Скрипт сборки .exe с помощью PyInstaller.

Использование:
  python build.py         # собрать
  python build.py clean   # удалить dist/build/файлы

Требования: PyInstaller, PyQt6
"""
import subprocess
import sys
from pathlib import Path


def build_exe():
    print("🔨 СБОРКА DESKTOP ПРИЛОЖЕНИЯ")
    current_dir = Path(__file__).parent
    app_name = "CompetitionMonitor"

    # Проверяем PyInstaller
    try:
        import PyInstaller  # noqa: F401
        print(f"   ✓ PyInstaller доступен")
    except Exception:
        print("   ✗ PyInstaller не найден — установите: pip install pyinstaller")
        return

    pyinstaller_args = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", app_name,
        "main.py",
        "--hidden-import", "PyQt6",
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui",
    ]

    print("\n🚀 Запуск PyInstaller (это может занять время)...")
    result = subprocess.run(pyinstaller_args, cwd=current_dir)
    if result.returncode != 0:
        print("❌ PyInstaller вернул ошибку")
        return

    exe_path = current_dir / "dist" / f"{app_name}.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ Сборка завершена: {exe_path} ({size_mb:.1f} MB)")
    else:
        print("❌ .exe файл не найден в dist/")


def clean():
    from shutil import rmtree
    current_dir = Path(__file__).parent
    for p in [current_dir / 'build', current_dir / 'dist', current_dir / f"{current_dir.name}.spec"]:
        if p.exists():
            print(f"Удаляю: {p}")
            try:
                if p.is_file():
                    p.unlink()
                else:
                    rmtree(p)
            except Exception as e:
                print(f"Ошибка удаления {p}: {e}")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        clean()
    else:
        build_exe()
