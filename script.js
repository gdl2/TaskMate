// Get references to the chatbot elements
const chatbot = document.getElementById('chatbot');
const output = document.getElementById('output');
const input = document.getElementById('message-input');
const steps = document.getElementById("steps");

// Add an event listener to the input field to detect Enter key presses
input.addEventListener('keyup', (event) => {
    if (event.key === 'Enter') {
        sendMessage(input.value);
    }
});

// Save chat history
const saveChatButton = document.getElementById('saveChat');
saveChatButton.addEventListener('click', saveChat);
function saveChat() {
  const xhr = new XMLHttpRequest();
  xhr.open('POST', 'http://127.0.0.1:5000/save_history');
  xhr.send();
};

// Reset chat history
resetChat.addEventListener('click', function() {
    chrome.storage.local.remove(['chatHistory'], function() {
        var error = chrome.runtime.lastError;
        if (error) {
            console.error(error);
        }
        else {
            console.log("Successfully cleared chat history.");
        }
    });

    // Send an AJAX request to the backend to reset chat history
    const xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:5000/clear_history');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = () => {
        if (xhr.status === 200) {
            output.innerHTML = '';
            steps.innerHTML = '';
        } else {
            console.error('Error getting response from chatbot');
        }
    };
    xhr.send(JSON.stringify({ message: "SUCCESS" }));
});

// Load past chat history when popup opens
chrome.storage.local.get('chatHistory', function(data) {
    if (data.chatHistory !== undefined) {
        console.log("Retrieved chat history.");
        console.log(data);
        output.innerHTML = data.chatHistory;
    } 
    else {
      console.log('The key does not exist in the storage.');
    }
});

// Function to get the HTML content of a tab
function getTabHTML(tab) {
    return new Promise(function(resolve, reject) {
      // Get the HTML content of the tab
      chrome.tabs.sendMessage(tab.id, { action: "getHTML" })
      .then(function(response) {
        // Resolve with the HTML content
        resolve(response.html);
      })
      .catch(function(error) {
        // Reject with the error object
        reject(error);
      });
    });
}  

// Get active tab
function getActiveTab(callback) {
    chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
      if (tabs && tabs.length) {
        callback(null, tabs[0]);
      } else {
        callback(new Error('No active tab found'));
      }
    });
  }

// Get HTML of tab
function getHtml(tab, callback) {
    chrome.tabs.executeScript(tab.id, { code: 'document.documentElement.outerHTML' }, function(result) {
      const html = result && result.length && result[0];
      if (html) {
        callback(null, html);
      } else {
        callback(new Error('Unable to get HTML'));
      }
    });
  }
  

// Save lst_steps as global variable
var lst_steps;

// Set the initial step number
let stepNum = 0;

// Function to send a message to the chatbot and receive a response
function sendMessage(message) {
    // Display the user's message in the chatbot interface
    output.innerHTML += `<p class="user-message"><b>User:</b> ${message}</p>`;

    // Clear the input field
    input.value = '';
    
    // Async call to get active tab 
    getActiveTab(function(err, tab) {
        if (err) {
          console.error(err);
          return;
        }
        // Next get HTML of active tab
        getHtml(tab, function(err, html) {
            if (err) {
            console.error(err);
            return;
            }
            console.log(html);
            // Send an AJAX request to the backend to get a response from the chatbot
            const xhr = new XMLHttpRequest();
            xhr.open('POST', 'http://127.0.0.1:5000/get_response');
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onload = () => {
                if (xhr.status === 200) {
                    // Display the chatbot's response in the chatbot interface
                    const response = JSON.parse(xhr.responseText).response;
                    output.innerHTML += `<p class="bot-message"><b>Bot:</b> ${response}</p>`;

                    // Receive the javascript code from the bot, if any
                    const javascript_code = JSON.parse(xhr.responseText).javascript_code;
                    console.log(javascript_code);

                    // Check if javascript code returned in response
                    if (javascript_code !== null) {
                        // Inject the script into the page
                        chrome.tabs.executeScript(
                            {code: javascript_code},
                            // NOT SURE IF FOLLOWING CODE WORKS
                            (results) => {
                                console.log(results);
                                const frameId = results[0].frameId;
                                chrome.tabs.executeScript({code: '', frameId: frameId});    
                        });
                    };

                    // Check if step-by-step summary is found
                    const found_summary = JSON.parse(xhr.responseText).found_summary;
                    console.log(found_summary);
                                        
                    if (found_summary === true) {
                      console.log("summary found");
                      lst_steps = JSON.parse(xhr.responseText).lst_steps;
                      lst_steps = JSON.parse(lst_steps);
                      console.log(lst_steps);
                      const totalSteps = lst_steps.length;
                      steps.innerHTML = `Step <span id="currStepNum">${stepNum}</span>/${totalSteps}`;

                      // Add event listener to nextStep
                      input.addEventListener('keydown', function(event) {
                        if (event.key === 'Tab') {
                          console.log("next step being pressed");
                          // Increment the step number
                          stepNum++;

                          console.log(stepNum);

                          // Update the current step number in the HTML
                          const currStepNum = document.getElementById("currStepNum");
                          currStepNum.textContent = stepNum;

                          // Get the corresponding step element from lst_steps
                          const step = lst_steps[stepNum - 1];

                          // Paste the description into the input field
                          input.value = `Let's do step ${stepNum} of the summary`;
                          event.preventDefault();
                        }
                      });
                    };

                    // Scroll to the bottom of the output container
                    output.scrollTop = output.scrollHeight;

                    // Save the chat history data to storage
                    var chatHistory = output.innerHTML;
                    chrome.storage.local.set({'chatHistory': chatHistory}, function() {
                        console.log('Chat history in Chrome memory.');
                        console.log(chatHistory);
                    });
                } else {
                    console.error('Error getting response from chatbot');
                }
            };

            xhr.send(JSON.stringify({ message: message, html: html }));
        });
    });
}
