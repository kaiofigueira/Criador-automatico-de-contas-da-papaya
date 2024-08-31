import subprocess

# Lista de pacotes do requirements.txt
packages = [
    "beautifulsoup4==4.9.3",
    "certifi==2020.12.5",
    "cffi==1.17.0",
    "chardet==4.0.0",
    "colorama==0.4.4",
    "cryptography==3.4.7",
    "fake-useragent==0.1.11",
    "httmock==1.4.0",
    "idna==2.10",
    "psutil==6.0.0",
    "pycparser==2.20",
    "pyOpenSSL==20.0.1",
    "python-dateutil==2.8.1",
    "requests==2.25.1",
    "selenium==3.141.0",
    "six==1.15.0",
    "soupsieve==2.2.1",
    "urllib3==1.26.4",
    "ipykernel",
    "request-randomizer==1.3.2"

]

for package in packages:
    print(f"Installing {package}...")
    try:
        subprocess.run(
            ["pip", "install", package],
            check=True
        )
        print(f"{package} installed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}.")
        print(f"Error: {e}\n")
        break
