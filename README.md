> [!CAUTION]
> The only official place to download Focuslock are this GitHub repository and through the links provided through [discord](https://discord.gg/n5ydyJtJst) . Any other websites offering downloads or claiming to be us are not controlled by us.

> [!WARNING]
> Once you start there is no going back, so once you before you set the timer make sure you are ready 

> [!TIP]
> This version is only for Windows, get the apk at [Focus-Lock Android](https://github.com/psycho980/focuslock-android)

<div align="center">

[![Downloads][shield-repo-releases]][repo-releases]
[![Version][shield-repo-latest]][repo-latest]
[![Discord][shield-discord-server]][discord-invite]

</div>

----

# FocusLock

FocusLock is a study monitoring application that helps users maintain focus during study sessions by detecting and closing non-study-related applications using AI-powered content analysis.

## Features
- Customizable study duration
- Automatic closing of non-study applications
- Modern dark-themed GUI
- Activity logging

## Installation

### From Installer
1. Download the [latest release](https://github.com/psycho980/FocusLock/releases/latest) from the [releases page](https://github.com/psycho980/FocusLock/releases)
2. Run the installer (requires administrator privileges)
3. Follow the installation wizard

### From Source
1. Clone the repository
```bash
git clone https://github.com/psycho980/FocusLock.git
```
2. Install required package
```bash
pip install -r requirements.txt
```
3. Run the application
```bash
python focuslock.py
```
## Building from Source

### Prerequisites
- Python 3.8 or higher
- PyInstaller
- Inno Setup (for creating installer)

### Build Steps
1. Install build dependencies
```bash
pip install pyinstaller
```
2. Build executable
```bash
pyinstaller focuslock.spec
```

3. Create installer (optional)
- Install Inno Setup
- Open `FocusLock.iss` in Inno Setup Compiler
- Click Compile or press F9

## Usage

1. Launch FocusLock (requires administrator privileges)
2. Set your desired study duration in hours and minutes
3. Click "Start Monitoring"
4. The application will run in the system tray
5. View logs anytime using the "View Logs" button

## Configuration

The application creates a config file at `%USERPROFILE%\FocusLock\config.json` where you can customize:
- Screenshot interval
- Ignored processes

## Requirements

- Windows 10/11
- Administrator privileges
- 4GB RAM minimum
- Internet connection (first run only, for model download)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern GUI
- [Salesforce/BLIP](https://github.com/salesforce/BLIP) for the VQA model

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

[shield-repo-releases]: https://img.shields.io/github/downloads/pscyho980/focuslock/latest/total?color=981bfe
[shield-repo-latest]:   https://img.shields.io/github/v/release/psycho980/focuslock?color=7a39fb

[shield-discord-server]: https://img.shields.io/discord/1335666371199238294?logo=discord&logoColor=white&label=discord&color=4d3dff

[repo-releases]: https://github.com/psycho980/focuslock/releases
[repo-latest]:   https://github.com/psycho980/focuslock/releases/latest

[discord-invite]:  https://discord.gg/n5ydyJtJst
