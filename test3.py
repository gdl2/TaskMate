import re

string = """Sure, here's a summary of our conversation with corresponding code for each step:

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

3. To remove the files "mario.zip" and "steam.zip" in the Terminal:

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

That's a summary of our conversation with the corresponding code for each step."""

steps = re.findall(r'\d+\.\s+(.*)', string)

for i, step in enumerate(steps):
    print(f"Step {i+1}: {step}")
