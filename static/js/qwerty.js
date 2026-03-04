const qwertyLayout = [
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
    ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
    ['Caps Lock', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'Enter'],
    ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
    ['Space']
];

// Map characters to their row/col in the layout
const charToPos = {};

qwertyLayout.forEach((row, rIndex) => {
    row.forEach((key, cIndex) => {
        // Store regular key
        charToPos[key] = { r: rIndex, c: cIndex };

        // Store shifted version if applicable
        if (key.length === 1 && key.match(/[a-z]/)) {
            charToPos[key.toUpperCase()] = { r: rIndex, c: cIndex };
        }
    });
});

const shiftMap = {
    '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8', '(': '9', ')': '0',
    '{': '[', '}': ']', '"': "'", '<': ',', '>': '.', '?': '/', '+': '=', '_': '-', ':': ';', '|': '\\', '~': '`'
};

Object.entries(shiftMap).forEach(([shifted, original]) => {
    if (charToPos[original]) {
        charToPos[shifted] = charToPos[original];
    }
});
