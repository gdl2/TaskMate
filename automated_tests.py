from selenium import webdriver
import requests
import time
import json

# Define the URL and the number of times to run the script
url = 'http://127.0.0.1:8080/html/miniwob/terminal.html'
num_runs = 100

# Define lists to store the rewards and times
rewards = []
times = []

# Define the driver and open the URL
driver = webdriver.Chrome()

for i in range(num_runs):
    # Navigate to task
    driver.get(url)

    # Bring the Chrome window to the foreground
    driver.switch_to.window(driver.window_handles[0])

    # Reset stepNum
    stepNum = 0

    # Get the HTML of the page
    page_html = driver.execute_script("return document.documentElement.outerHTML")

    # Send the page HTML and user message to the server
    response = requests.post('http://127.0.0.1:5000/get_response',
                            json={'html': page_html, 'message': 'complete_task'})

    print(response.json())
    
    # See if summary is found
    lst_steps = response.json()['lst_steps']

    # Parse JSON list
    lst_steps = json.loads(lst_steps)

    # Iterate through steps of summary
    while stepNum < len(lst_steps):
        # Get the HTML of the page
        page_html = driver.execute_script("return document.documentElement.outerHTML")

        # Create user message
        message = "Let's do step {} of the step-by-step summary provided by the user".format(stepNum+1)
        print(message)
            
        # Send the page HTML and user message to the server
        response = requests.post('http://127.0.0.1:5000/get_response',
                                json={'html': page_html, 'message': message})

        # Get the JavaScript code from the response
        js_code = response.json()['javascript_code']
        print(js_code)

        # Execute the JavaScript code in the browser
        if js_code:
            # Track time before it disappears
            if stepNum == len(lst_steps)-1:
                # Get the current time and total time and store the current time in the times list
                time_element = driver.find_element("id", "timer-countdown")
                curr_time = time_element.text.split('/')[0]
                if curr_time == "-":
                    curr_time = -1
                else:
                    curr_time = float(curr_time)
                times.append(curr_time)
                print("Time: ", curr_time)

            driver.execute_script(js_code)
        
        # Increment steps
        stepNum += 1

        if stepNum > 1:
            print(driver.find_element("id", "query").text)

        # Pause between steps
        time.sleep(5)

    # Reset the chat history
    response = requests.post('http://127.0.0.1:5000/clear_history')
    
    # Get the reward and store it in the rewards list
    reward_element = driver.find_element("id", "reward-last")
    if reward_element.text == "-":
        reward = -1
    else:
        reward = float(reward_element.text)    
    rewards.append(reward)
    print("Reward: ", reward)

print("Rewards: ", rewards)
print("Times: ", times)

# Quit the driver
driver.quit()
