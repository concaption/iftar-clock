# Iftar Clock

A minimal Python application that displays a countdown to Iftar (sunset) time in the bottom right corner of your screen.

## Features

- Automatic location detection using IP address
- Sunset time retrieval for accurate Iftar timing
- Minimal UI showing only the countdown
- System tray icon with the countdown timer
- Saves sunset times locally to reduce API calls
- Position the timer in the bottom right corner of your screen
- Comprehensive logging system for troubleshooting

## Installation

### Using as a Python Application

1. Clone the repository:
```bash
git clone https://github.com/concaption/iftar-clock.git
cd iftar-clock
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Building as a Standalone Executable

#### Automatic Method (Windows)

1. Run the installation script:
```
install.bat
```

2. The script will install the required dependencies and offer to build the executable.
3. After building, you'll find `IftarClock.exe` in the project folder.

#### Manual Method

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Run the build script:
```bash
python build_exe.py
```

3. The executable will be created in the `dist` folder and copied to the project root.

## Usage

### Running as Python Script

```bash
python main.py
```

### Running as Executable

Simply double-click `IftarClock.exe` to run the application.

A small digital clock will appear in the bottom-right corner of your screen showing the countdown to Iftar time.

### Controls

- **Click and drag** to move the clock anywhere on your screen
- **Right-click** to open the menu:
  - **Refresh** - Force update of the Iftar time
  - **Toggle Border** - Show or hide the window border
  - **Show logs** - Open the directory containing log files
  - **Exit** - Close the application

## Logging

The application maintains detailed logs that can be helpful for troubleshooting:

- Log files are stored in `~/.iftar_clock/` directory (user's home folder)
- Each day has its own log file named `iftar_clock_YYYYMMDD.log`
- You can access logs via the right-click menu by selecting "Show logs"

## Troubleshooting

If you experience issues with incorrect times:

1. Right-click the clock and select "Refresh" to fetch new data
2. If that doesn't work, run `clear_cache.py` to reset the cached sunset data
3. Check the log files for more detailed information

## How it works

The application:
1. Detects your location using the IP address
2. Fetches the sunset time for your location
3. Displays a countdown timer to sunset
4. Caches sunset times to avoid unnecessary API calls

## Attribution

This project uses the following free APIs:
- [Sunrise-Sunset API](https://sunrise-sunset.org/api) for sunset times
- [ipapi.co](https://ipapi.co/) for location detection

## License

[MIT License](LICENSE)
