# Browsinator

Browsinator is a Python library for programmatically controlling and interacting with a web browser using the Chrome DevTools Protocol.


## Installation

To install Browsinator, you'll need Python 3.6 or later. You can install it using pip:

```bash
pip install browsinator
```

## Usage

Here's a basic example of how to use Browsinator:

```python
from browsinator import Browser

# Start Chrome (you can optionally specify the path to Chrome executable)
Browser.start()

# Connect to the browser
browser = Browser()
browser.connect()
```

You can also customize the Chrome startup:

```python
# Start Chrome with custom options
Browser.start(
    path="/path/to/chrome",  # Custom Chrome executable path
    minimized=False,         # Start Chrome in normal window (not minimized)
    debug_port=9223          # Use a custom debugging port
)

# Connect to the browser
browser = Browser()
browser.connect()
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
