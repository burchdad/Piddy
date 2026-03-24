"""Quick test of the action parser with the actual Ollama output pattern."""
from src.agent.action_parser import parse_file_actions

test = """### File Structure

```
weather_dashboard/
\u251c\u2500\u2500 app.py
\u251c\u2500\u2500 config.py
\u251c\u2500\u2500 models.py
\u251c\u2500\u2500 routes.py
\u251c\u2500\u2500 templates/
\u2502   \u251c\u2500\u2500 base.html
\u2502   \u251c\u2500\u2500 index.html
\u2502   \u2514\u2500\u2500 forecast.html
\u251c\u2500\u2500 static/
\u2502   \u251c\u2500\u2500 css/
\u2502   \u2502   \u2514\u2500\u2500 styles.css
\u2502   \u2514\u2500\u2500 js/
\u2502       \u2514\u2500\u2500 script.js
\u2514\u2500\u2500 requirements.txt
```

### Files

===FILE: weather_dashboard/app.py===
```python
from flask import Flask
app = Flask(__name__)
```

===FILE: weather_dashboard/config.py===
```python
SECRET = "test_secret"
```

===FILE: weather_dashboard/models.py===
```python
class Weather:
    pass
```

===FILE: weather_dashboard/routes.py===
```python
from flask import Blueprint
main_bp = Blueprint("main", __name__)
```

### Templates

#### base.html
```html
<!DOCTYPE html><html><body>{%% block content %%}{%% endblock %%}</body></html>
```

#### index.html
```html
{%% extends "base.html" %%}{%% block content %%}<h1>Weather</h1>{%% endblock %%}
```

#### forecast.html
```html
{%% extends "base.html" %%}{%% block content %%}<h2>Forecast</h2>{%% endblock %%}
```

### Static Files

#### styles.css
```css
body { font-family: Arial; }
```

#### script.js
```javascript
function searchWeather() { console.log("search"); }
```
"""

actions = parse_file_actions(test)
print(f"Total files parsed: {len(actions)}")
for a in actions:
    print(f"  {a['path']:55s} ({len(a['content'])} bytes)")

# Assertions
assert len(actions) >= 9, f"Expected at least 9 files, got {len(actions)}"
paths = [a["path"] for a in actions]
assert "weather_dashboard/app.py" in paths
assert "weather_dashboard/config.py" in paths
assert any("base.html" in p for p in paths)
assert any("styles.css" in p for p in paths)
assert any("script.js" in p for p in paths)
# Check templates got proper paths
base_path = next(p for p in paths if "base.html" in p)
assert "weather_dashboard" in base_path, f"base.html should be under weather_dashboard, got: {base_path}"
print("\nAll assertions passed!")
