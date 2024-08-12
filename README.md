# Browsinator

Browsinator is a Python library for programmatically controlling and interacting with a web browser using the Chrome DevTools Protocol.


## Installation

To install Browsinator, you'll need Python 3.6 or later. You can install it using pip:

```bash
pip install browsinator
```

## Usage

Here's a basic example of how to use Browsinator:

Start Chrome with the following command:

### MacOS
```bash
open -a "Google Chrome" --args --start-minimized --remote-allow-origins=http://localhost:9222 --user-data-dir=/tmp/dir1 --disable-gpu --remote-debugging-port=9222
```

### Linux
```bash
google-chrome --start-minimized --remote-allow-origins=http://localhost:9222 --user-data-dir=/tmp/dir1 --disable-gpu --remote-debugging-port=9222
```

### Windows
```bash
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --start-minimized --remote-allow-origins=http://localhost:9222 --user-data-dir=/tmp/dir1 --disable-gpu --remote-debugging-port=9222
```

Then you can use Browsinator to control the browser:

```python
browser = Browser()
```

#### Navigate to a URL
```python
browser.load("https://example.com", wait=True)
```

#### Run JavaScript
```python
result = browser.run_script_sync_get_result("document.title")
print(f"Page title: {result}")
```

#### Monitor network traffic
```python
browser.match_network("api/data", lambda req, res, data: print(f"API data: {data}"))
browser.monitor_network()
```

#### Simulate user input
```python
browser.keyboard_type("Hello, World!")
browser.keyboard_press_enter()
browser.mouse_click_selector("#submit-button")
```

#### Close the browser
```python
browser.close()
```