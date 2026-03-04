document.addEventListener('DOMContentLoaded', () => {
    const textDisplay = document.getElementById('text-display');
    const hiddenInput = document.getElementById('hidden-input');
    const typingArea = document.getElementById('typing-area');
    const keyboardContainer = document.getElementById('keyboard-container');
    const wpmEl = document.getElementById('wpm');
    const accuracyEl = document.getElementById('accuracy');
    const streakEl = document.getElementById('streak');
    const modalOverlay = document.getElementById('modal-overlay');
    const finalWpmEl = document.getElementById('final-wpm');
    const finalAccuracyEl = document.getElementById('final-accuracy');
    const restartBtn = document.getElementById('restart-btn');
    const loadingEl = document.getElementById('loading');
    const aiModeSelect = document.getElementById('ai-mode-select');
    const aiProgressBar = document.getElementById('ai-progress-bar');
    const playerProgressBar = document.getElementById('player-progress-bar');
    const modalTitle = modalOverlay.querySelector('h2');

    let currentText = "";
    let startTime = null;
    let errors = 0;
    let streak = 0;
    let maxStreak = 0;
    let isFinished = false;
    let aiProgress = 0;
    let aiRunning = false;
    let aiInterval = null;
    let aiFinished = false;

    // Initialize Keyboard
    function renderKeyboard() {
        keyboardContainer.innerHTML = '';
        qwertyLayout.forEach((row, rIndex) => {
            const rowEl = document.createElement('div');
            rowEl.className = 'kb-row';

            row.forEach((key, cIndex) => {
                const keyEl = document.createElement('div');
                keyEl.className = 'key';
                keyEl.textContent = key === 'Space' ? '' : key;
                keyEl.dataset.r = rIndex;
                keyEl.dataset.c = cIndex;

                if (key.length > 1) keyEl.classList.add('special');
                if (key === 'Space') keyEl.classList.add('space');

                rowEl.appendChild(keyEl);
            });

            keyboardContainer.appendChild(rowEl);
        });
    }

    function highlightKey(char) {
        // Clear previous highlights
        document.querySelectorAll('.key.active').forEach(el => el.classList.remove('active'));

        if (!char) return;

        const pos = charToPos[char];
        if (pos) {
            const keyEl = document.querySelector(`.key[data-r="${pos.r}"][data-c="${pos.c}"]`);
            if (keyEl) keyEl.classList.add('active');
        } else if (char === ' ') {
            const spaceKey = document.querySelector('.key.space');
            if (spaceKey) spaceKey.classList.add('active');
        }
    }

    // Game Logic
    // Stories Local Fallback
    const STORIES = [
        "Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do: once or twice she had peeped into the book her sister was reading, but it had no pictures or conversations in it, 'and what is the use of a book,' thought Alice 'without pictures or conversation?'",
        "You will rejoice to hear that no disaster has accompanied the commencement of an enterprise which you have regarded with such evil forebodings. I arrived here yesterday, and my first task is to assure my dear sister of my welfare and increasing confidence in the success of my undertaking.",
        "To Sherlock Holmes she is always the woman. I have seldom heard him mention her under any other name. In his eyes she eclipses and predominates the whole of her sex. It was not that he felt any emotion akin to love for Irene Adler.",
        "In my younger and more vulnerable years my father gave me some advice that I've been turning over in my mind ever since. 'Whenever you feel like criticizing any one,' he told me, 'just remember that all the people in this world haven't had the advantages that you've had.'",
        "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife. However little known the feelings or views of such a man may be on his first entering a neighbourhood.",
        "Call me Ishmael. Some years ago, having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world."
    ];

    async function loadGame() {
        isFinished = false;
        hiddenInput.value = '';
        currentText = '';
        startTime = null;
        errors = 0;
        streak = 0;
        maxStreak = 0;

        // Reset UI
        textDisplay.innerHTML = '';
        wpmEl.textContent = '0';
        accuracyEl.textContent = '100%';
        streakEl.textContent = '0';
        modalOverlay.classList.add('hidden');
        loadingEl.classList.remove('hidden');

        // Reset AI
        aiProgress = 0;
        aiRunning = false;
        aiFinished = false;
        clearInterval(aiInterval);
        updateProgressBars();

        // Static Pages Strategy: Use local stories
        setTimeout(() => {
            currentText = STORIES[Math.floor(Math.random() * STORIES.length)];
            renderText();
            highlightKey(currentText[0]);
            hiddenInput.focus();
            loadingEl.classList.add('hidden');
        }, 500);
    }

    function renderText() {
        const inputVal = hiddenInput.value;
        let html = '';

        for (let i = 0; i < currentText.length; i++) {
            const char = currentText[i];
            let className = 'char';

            if (i < inputVal.length) {
                if (inputVal[i] === char) {
                    className += ' correct';
                } else {
                    className += ' incorrect';
                }
            } else if (i === inputVal.length) {
                className += ' current';
            }

            html += `<span class="${className}">${char}</span>`;
        }

        textDisplay.innerHTML = html;
    }

    function updateStats() {
        const inputVal = hiddenInput.value;
        const timeElapsed = (Date.now() - startTime) / 1000 / 60; // minutes

        if (timeElapsed > 0) {
            const wpm = Math.round((inputVal.length / 5) / timeElapsed);
            wpmEl.textContent = wpm;
        }

        const totalAttempts = inputVal.length + errors;
        const accuracy = totalAttempts > 0
            ? Math.round((inputVal.length / totalAttempts) * 100)
            : 100;
        accuracyEl.textContent = `${accuracy}%`;

        streakEl.textContent = streak;
    }

    function finishGame() {
        isFinished = true;
        aiRunning = false;
        clearInterval(aiInterval);

        finalWpmEl.textContent = wpmEl.textContent;
        finalAccuracyEl.textContent = accuracyEl.textContent;

        const mode = aiModeSelect.value;
        if (mode !== 'Solo') {
            if (aiFinished && hiddenInput.value.length < currentText.length) {
                modalTitle.textContent = "AI Won! Keep practicing.";
                modalTitle.style.color = "#ef4444";
            } else if (!aiFinished && hiddenInput.value.length >= currentText.length) {
                modalTitle.textContent = "Victory! You beat the AI.";
                modalTitle.style.color = "#10b981";
            } else {
                modalTitle.textContent = "It's a tie!";
                modalTitle.style.color = "#ffffff";
            }
        } else {
            modalTitle.textContent = "Session Complete!";
            modalTitle.style.color = "#ffffff";
        }

        modalOverlay.classList.remove('hidden');
    }

    function updateProgressBars() {
        if (!currentText) return;
        const playerRatio = (hiddenInput.value.length / currentText.length) * 100;
        playerProgressBar.style.width = `${playerRatio}%`;

        const aiRatio = (aiProgress / currentText.length) * 100;
        aiProgressBar.style.width = `${aiRatio}%`;
    }

    function startAI() {
        const mode = aiModeSelect.value;
        if (mode === 'Solo') return;

        const speeds = { 'Easy': 25, 'Normal': 50, 'Hard': 85 };
        const wpm = speeds[mode] || 50;
        const charsPerSec = (wpm * 5) / 60;

        aiRunning = true;
        aiInterval = setInterval(() => {
            if (isFinished) {
                clearInterval(aiInterval);
                return;
            }
            aiProgress++;
            updateProgressBars();
            if (aiProgress >= currentText.length) {
                aiFinished = true;
                clearInterval(aiInterval);
                finishGame();
            }
        }, 1000 / charsPerSec);
    }

    // Event Listeners
    hiddenInput.addEventListener('input', (e) => {
        if (isFinished) return;

        const val = hiddenInput.value;

        if (!startTime) {
            startTime = Date.now();
            startAI();
        }

        // Check latest char
        if (val.length > 0) {
            const lastIndex = val.length - 1;
            const expected = currentText[lastIndex];
            const typed = val[lastIndex];

            if (expected === typed) {
                streak++;
                if (streak > maxStreak) maxStreak = streak;
            } else {
                streak = 0;
                errors++;
            }
        }

        renderText();
        updateStats();
        updateProgressBars();

        // Highlight next key
        if (val.length < currentText.length) {
            highlightKey(currentText[val.length]);
        } else {
            finishGame();
        }
    });

    // Prevent default behavior for some keys to keep focus
    hiddenInput.addEventListener('keydown', (e) => {
        // Allow backspace
        if (e.key === 'Backspace') return;

        // Prevent moving cursor manually
        if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(e.key)) {
            e.preventDefault();
        }
    });

    typingArea.addEventListener('click', () => {
        hiddenInput.focus();
    });

    aiModeSelect.addEventListener('change', loadGame);

    restartBtn.addEventListener('click', loadGame);

    // Initial Setup
    renderKeyboard();
    loadGame();
});
