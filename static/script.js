const promptInput = document.getElementById("promptInput");

const generateBtn = document.getElementById("generateBtn");

const generateText = document.getElementById("generateText");

const generateIcon = document.getElementById("generateIcon");

const characterCount = document.getElementById("characterCount");

const typingStatus = document.getElementById("typingStatus");

const previewFrame = document.getElementById("previewFrame");

const emptyPreview = document.getElementById("emptyPreview");

const previewStatus = document.getElementById("previewStatus");

const clearBtn = document.getElementById("clearBtn");

const refreshBtn = document.getElementById("refreshBtn");

const openBtn = document.getElementById("openBtn");

const copyBtn = document.getElementById("copyBtn");

const toast = document.getElementById("toast");

const exampleButtons = document.querySelectorAll(".example");


let generatedHTML = "";

let debounceTimer = null;

let lastGeneratedPrompt = "";

let isGenerating = false;


/*
====================================
CHARACTER COUNT
====================================
*/

function updateCharacterCount() {

    const length = promptInput.value.length;

    characterCount.textContent =
        `${length} characters`;
}

promptInput.addEventListener(
    "input",
    updateCharacterCount
);


/*
====================================
LIVE TYPING GENERATION
====================================
*/

promptInput.addEventListener("input", () => {

    clearTimeout(debounceTimer);

    const prompt = promptInput.value.trim();

    if (!prompt) {

        typingStatus.textContent = "Ready";

        return;
    }

    typingStatus.textContent = "Typing...";

    /*
    Wait 1200ms after the user stops typing.
    */

    debounceTimer = setTimeout(() => {

        if (prompt !== lastGeneratedPrompt) {

            generateWebsite(prompt);

        }

    }, 1200);

});


/*
====================================
GENERATE BUTTON
====================================
*/

generateBtn.addEventListener("click", () => {

    const prompt = promptInput.value.trim();

    if (!prompt) {

        showToast("Please enter a prompt");

        return;
    }

    generateWebsite(prompt);

});


/*
====================================
GENERATE WEBSITE
====================================
*/

async function generateWebsite(prompt) {

    if (isGenerating) {
        return;
    }

    isGenerating = true;

    lastGeneratedPrompt = prompt;

    generateBtn.disabled = true;

    generateIcon.textContent = "◌";

    generateText.textContent = "Generating...";

    typingStatus.textContent = "AI generating...";

    previewStatus.textContent =
        "Generating your website...";


    try {

        const response = await fetch(
            "/generate",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    prompt: prompt
                })
            }
        );


        const data = await response.json();


        if (!response.ok || !data.success) {

            throw new Error(
                data.error || "Generation failed"
            );

        }


        generatedHTML = data.html;


        /*
        Display generated HTML inside iframe
        */

        previewFrame.srcdoc = generatedHTML;

        previewFrame.style.display = "block";

        emptyPreview.style.display = "none";


        previewStatus.textContent =
            "Generated successfully";


        typingStatus.textContent =
            "Generated ✓";


    } catch (error) {

        console.error(error);

        previewStatus.textContent =
            "Generation failed";

        typingStatus.textContent =
            "Error";

        showToast(error.message);

    } finally {

        isGenerating = false;

        generateBtn.disabled = false;

        generateIcon.textContent = "✦";

        generateText.textContent =
            "Generate Website";

    }

}


/*
====================================
CLEAR
====================================
*/

clearBtn.addEventListener("click", () => {

    promptInput.value = "";

    generatedHTML = "";

    lastGeneratedPrompt = "";

    clearTimeout(debounceTimer);

    previewFrame.srcdoc = "";

    previewFrame.style.display = "none";

    emptyPreview.style.display = "flex";

    characterCount.textContent =
        "0 characters";

    typingStatus.textContent =
        "Ready";

    previewStatus.textContent =
        "Your generated website appears here";

});


/*
====================================
REFRESH PREVIEW
====================================
*/

refreshBtn.addEventListener("click", () => {

    if (!generatedHTML) {

        showToast("Nothing to refresh");

        return;
    }

    previewFrame.srcdoc = "";

    setTimeout(() => {

        previewFrame.srcdoc =
            generatedHTML;

    }, 50);

});


/*
====================================
OPEN PREVIEW IN NEW TAB
====================================
*/

openBtn.addEventListener("click", () => {

    if (!generatedHTML) {

        showToast("Generate a website first");

        return;
    }


    const blob = new Blob(
        [generatedHTML],
        {
            type: "text/html"
        }
    );


    const url = URL.createObjectURL(blob);

    window.open(url, "_blank");

});


/*
====================================
COPY GENERATED CODE
====================================
*/

copyBtn.addEventListener("click", async () => {

    if (!generatedHTML) {

        showToast("No generated code");

        return;
    }


    try {

        await navigator.clipboard.writeText(
            generatedHTML
        );

        showToast("HTML copied!");

    } catch (error) {

        showToast(
            "Could not copy code"
        );

    }

});


/*
====================================
EXAMPLE BUTTONS
====================================
*/

exampleButtons.forEach(button => {

    button.addEventListener("click", () => {

        const examplePrompt =
            button.dataset.prompt;

        promptInput.value =
            examplePrompt;

        updateCharacterCount();

        generateWebsite(
            examplePrompt
        );

    });

});


/*
====================================
TOAST
====================================
*/

function showToast(message) {

    toast.textContent = message;

    toast.classList.add("show");

    setTimeout(() => {

        toast.classList.remove("show");

    }, 2500);

}


/*
====================================
INITIALIZE
====================================
*/

updateCharacterCount();
