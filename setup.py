from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but some modules need manual inclusion
build_exe_options = {
    "packages": ["os", "pygame", "numpy", "pyaudio", "scipy"],  # Include any tricky libraries here
    "excludes": ["tkinter"],  # Exclude libraries not used
    "include_files": ["Blurry_circle.png", "Halftone Font.ttf"]  # Include non-Python files
}

base = None

setup(
    name="Matrix Rain Simulator",
    version="0.1",
    description="My Matrix Rain application!",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)]
)