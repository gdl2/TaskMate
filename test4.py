import pickle
import os

query_actions_mapping = {}

# check is mapping exists on disk
if os.path.isfile("query_actions_mapping.pickle"):
    # deserialize the dictionary from the file
    with open("query_actions_mapping.pickle", 'rb') as f:
        query_actions_mapping = pickle.load(f)

print(len(query_actions_mapping))

query_actions_mapping["HTML: <html><head>\n<title>Terminal Task</title>\n</head>\n<body>\n<div id=\"wrap\">\n<div id=\"query\"></div>\n<div id=\"area\"></div>\n</div>\n<canvas id=\"click-canvas\"></canvas><div id=\"reward-display\">\n<div class=\"info\">\n<label>Last reward:</label>\n<span id=\"reward-last\">-</span>\n</div>\n<div class=\"info\">\n<label>Last 10 average:</label>\n<span id=\"reward-avg\">-</span>\n</div>\n<div class=\"info\">\n<label>Time left:</label>\n<span id=\"timer-countdown\">-</span>\n</div>\n<div class=\"info\">\n<label>Episodes done:</label>\n<span id=\"episode-id\">0</span>\n</div>\n</div><div id=\"sync-task-cover\">START</div></body></html>\nUser command: press Start"] = '''
Objective: Use the terminal below to delete a file ending with the extension <span class="bold>.zip</span>
Sure, here's a summary of our conversation with corresponding code for each step:

1. To press the Start button, simulate a click event on the element with id "sync-task-cover".

```
document.getElementById("sync-task-cover").click();
```

2. To type "ls" in the Terminal's active-input element and then simulate a press of the enter key:

```
var activeInput = document.getElementById("active-input");
activeInput.textContent = "ls";
var evt = new KeyboardEvent("keydown", {
  key: "Enter",
  code: "Enter",
  keyCode: 13,
  view: window,
  bubbles: true,
  cancelable: true
});
var terminalTarget = document.getElementById("terminal-target");
terminalTarget.dispatchEvent(evt);
```

3. Note: rm argument '*' not supported. We need to use the exact file name. To remove the files "mario.zip" and "steam.zip" in the Terminal:

```
var activeInput = document.getElementById("active-input");
activeInput.textContent = "rm mario.zip steam.zip";
var evt = new KeyboardEvent("keydown", {
  key: "Enter",
  code: "Enter",
  keyCode: 13,
  view: window,
  bubbles: true,
  cancelable: true
});
var terminalTarget = document.getElementById("terminal-target");
terminalTarget.dispatchEvent(evt);
```

That's a summary of our conversation with the corresponding code for each step.'''

print(len(query_actions_mapping))

# Disk the mapping to disk
with open("query_actions_mapping.pickle", "wb") as f:
    pickle.dump(query_actions_mapping, f)