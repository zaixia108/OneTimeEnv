import requests
import sys

def main():
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "World"
    print(f"Hello, {name}!")

    try:
        response = requests.get("https://www.example.com")
        print(f"Successfully accessed example.com. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to access example.com: {e}")

if __name__ == "__main__":
    main()