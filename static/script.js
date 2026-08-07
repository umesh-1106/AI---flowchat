const chatBox = document.getElementById("chatBox");
const prompt = document.getElementById("prompt");
const sendBtn = document.getElementById("sendBtn");
const clearBtn = document.getElementById("clearBtn");
const previewFrame = document.getElementById("previewFrame");

// Send on button click
sendBtn.addEventListener("click", sendMessage);

// Send on Enter (Shift+Enter for new line)
prompt.addEventListener("keydown", function(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Clear chat
clearBtn.addEventListener("click", async () => {

    chatBox.innerHTML = "";

    await fetch("/clear", {
        method: "POST"
    });

    previewFrame.srcdoc = "";

});


// Add a chat bubble
function addMessage(text, type) {

    const message = document.createElement("div");
    message.className = "message " + type;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.innerHTML = type === "user" ? "👤" : "🤖";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerText = text;

    if(type === "user"){
        message.appendChild(bubble);
        message.appendChild(avatar);
    }else{
        message.appendChild(avatar);
        message.appendChild(bubble);
    }

    chatBox.appendChild(message);

    chatBox.scrollTop = chatBox.scrollHeight;
}


// Send message to Flask
async function sendMessage() {

    const text = prompt.value.trim();

    if(text === "")
        return;

    addMessage(text, "user");

    prompt.value = "";

    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: text
            })

        });

        const data = await response.json();

        addMessage(data.reply, "ai");

        // Auto preview if AI returns HTML
        if (
            data.reply.includes("<html") ||
            data.reply.includes("<!DOCTYPE html") ||
            data.reply.includes("<body")
        ) {
            previewFrame.srcdoc = data.reply;
        }

    }
    catch(error){

        addMessage(
            "❌ Cannot connect to Flask/Ollama.\n\nMake sure:\n1. app.py is running\n2. Ollama is running",
            "ai"
        );

    }

}
