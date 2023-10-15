document.addEventListener('DOMContentLoaded', ()=>{
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages =document.getElementById('chat-messages');

    let loaderTimeout;

    hideLoader();

    function sendUserMessage(){
        const userMessage = userInput.value.trim();
        const searchWord = "images";
        const regex = new RegExp(`\\b${searchWord}\\b`);

        if (regex.test(userMessage)){
            if(userMessage === "") return;

            appendMessage('user', userMessage);

            loaderTimeout = setTimeout(() => {
                showLoader();
            }, 0);

            fetch('http://localhost:5000/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_input: userMessage,
                }),
            })
                .then((response) => response.json())
                .then((data) => {
                    // Cancel the loader timeout (response received)
                    console.log(data);
                    clearTimeout(loaderTimeout);
                    hideLoader();
                    let imgForPlace = extractLinksFromObject(data)
                    const messageDiv = document.createElement('div');
                    messageDiv.classList.add('message', 'bot');

                    // Create a message content element
                    const messageContentDiv = document.createElement('div');
                    messageContentDiv.classList.add('message-content');
                    messageContentDiv.innerHTML = `<a href="#" id="image-link">View Images</a>`;
                    messageContentDiv.addEventListener('click', (e)=>{
                        e.preventDefault();
                        openImageDialog(imgForPlace);
                    })
                    // Append the message content to the message container
                    messageDiv.appendChild(messageContentDiv);
                    // Append the message container to the chatMessages element
                    chatMessages.appendChild(messageDiv);
                    // Scroll to the bottom to show the latest message
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                })
                .catch((error) => {
                    console.error('Error:', error);
                    appendMessage('bot', "There is some issue at server side. Please try again after refreshing.");
                    // Hide the loader in case of an error
                    hideLoader();
                });

            // Clear the input field
            userInput.value = '';
            
        }else{
            if(userMessage === "") return;

            appendMessage('user', userMessage);

            loaderTimeout = setTimeout(() => {
                showLoader();
            }, 0);

            fetch('http://localhost:5000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_input: userMessage,
                }),
            })
                .then((response) => response.json())
                .then((data) => {
                    // Cancel the loader timeout (response received)
                    console.log(data);
                    clearTimeout(loaderTimeout);
                    hideLoader();
                    // Add chatbot's response to the chat display
                    const chatbotResponse = data.response;
                    appendMessage('bot', chatbotResponse);
                })
                .catch((error) => {
                    console.error('Error:', error);
                    appendMessage('bot', "There is some issue at server side. Please try again after refreshing.");
                    // Hide the loader in case of an error
                    hideLoader();
                });

            // Clear the input field
            userInput.value = '';
        }

        
    }

    function showLoader() {
        // Show the loader while waiting for the response
        const loader = document.createElement('div');
        loader.classList.add('dot-loader');
        chatMessages.appendChild(loader);
    }

    // Function to hide the loader
    function hideLoader() {
        // Remove the loader from the chat
        const loader = document.querySelector('.dot-loader');
        if (loader) {
            loader.remove();
        }
    }

    // Function to append a message to the chat
    function appendMessage(role, content) {
        // Create a message container
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', role);

        // Create a message content element
        const messageContentDiv = document.createElement('div');
        messageContentDiv.classList.add('message-content');
        messageContentDiv.innerText = content;

        // Append the message content to the message container
        messageDiv.appendChild(messageContentDiv);

        // Append the message container to the chatMessages element
        chatMessages.appendChild(messageDiv);

        // Scroll to the bottom to show the latest message
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Add a click event listener to the send button
    sendButton.addEventListener('click', sendUserMessage);

    // Add a keypress event listener to the user input field to allow sending with Enter key
    userInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendUserMessage();
        }
    });
})

// ----------------function to display images----------------------
function openImageDialog(images) {
    const imageDialog = document.getElementById('image-dialog');
    const imageContainer = document.getElementById('image-container');

    // Clear any previous images
    imageContainer.innerHTML = '';

    // images.forEach(imageUrl => {
        
    // });

    for(let i=0 ; i<images.length-1 ; i++){
        const image = document.createElement('img');
        const imageUrlWithoutComma = images[i].replace(',', '');
        image.setAttribute("src", imageUrlWithoutComma);
        console.log(images[i])
        imageContainer.appendChild(image);
    }

    // Show the dialog
    imageDialog.classList.remove('hidden');

    // Close the dialog when the close button is clicked
    document.getElementById('close-dialog').addEventListener('click', () => {
        imageDialog.classList.add('hidden');
    });
}

// ----------------Function to extract out links from the response---------------
function extractLinksFromObject(obj) {
    const links = [];
    
    // Check if the input object has an "answer" property
    if (obj && obj.answer) {
      // Split the "answer" string by newline characters to get an array of lines
      const lines = obj.answer.split('\n');
      
      // Iterate through the lines and extract links
      lines.forEach(line => {
        // Use a regular expression to match URLs
        const urlMatches = line.match(/\bhttps?:\/\/\S+/gi);
        if (urlMatches) {
          links.push(...urlMatches);
        }
      });
    }
    
    return links;
  }