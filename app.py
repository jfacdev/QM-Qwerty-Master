import random
import json
import urllib.request
import urllib.error
from flask import Flask, render_template, jsonify

app = Flask(__name__)

STORIES = [
    {
        "title": "Alice's Adventures in Wonderland",
        "content": "Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do: once or twice she had peeped into the book her sister was reading, but it had no pictures or conversations in it, 'and what is the use of a book,' thought Alice 'without pictures or conversation?' So she was considering in her own mind (as well as she could, for the hot day made her feel very sleepy and stupid), whether the pleasure of making a daisy-chain would be worth the trouble of getting up and picking the daisies, when suddenly a White Rabbit with pink eyes ran close by her."
    },
    {
        "title": "Frankenstein",
        "content": "You will rejoice to hear that no disaster has accompanied the commencement of an enterprise which you have regarded with such evil forebodings. I arrived here yesterday, and my first task is to assure my dear sister of my welfare and increasing confidence in the success of my undertaking. I am already far north of London, and as I walk in the streets of Petersburgh, I feel a cold northern breeze play upon my cheeks, which braces my nerves and fills me with delight. Do you understand this feeling? This breeze, which has travelled from the regions towards which I am advancing, gives me a foretaste of those icy climes."
    },
    {
        "title": "Dracula",
        "content": "3 May. Bistritz.—Left Munich at 8:35 P. M., on 1st May, arriving at Vienna early next morning; should have arrived at 6:46, but train was an hour late. Buda-Pesth seems a wonderful place, from the glimpse which I got of it from the train and the little I could walk through the streets. I feared to go very far from the station, as we had arrived late and would start as near the correct time as possible. The impression I had was that we were leaving the West and entering the East; the most western of splendid bridges over the Danube, which is here of noble width and depth, took us among the traditions of Turkish rule."
    },
    {
        "title": "The Adventures of Sherlock Holmes",
        "content": "To Sherlock Holmes she is always the woman. I have seldom heard him mention her under any other name. In his eyes she eclipses and predominates the whole of her sex. It was not that he felt any emotion akin to love for Irene Adler. All emotions, and that one particularly, were abhorrent to his cold, precise but admirably balanced mind. He was, I take it, the most perfect reasoning and observing machine that the world has seen, but as a lover he would have placed himself in a false position. He never spoke of the softer passions, save with a gibe and a sneer."
    },
    {
        "title": "The Great Gatsby",
        "content": "In my younger and more vulnerable years my father gave me some advice that I've been turning over in my mind ever since. 'Whenever you feel like criticizing any one,' he told me, 'just remember that all the people in this world haven't had the advantages that you've had.' He didn't say any more, but we've always been unusually communicative in a reserved way, and I understood that he meant a great deal more than that."
    },
    {
        "title": "Pride and Prejudice",
        "content": "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife. However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters."
    },
    {
        "title": "Moby Dick",
        "content": "Call me Ishmael. Some years ago—never mind how long precisely—having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world. It is a way I have of driving off the spleen and regulating the circulation. Whenever I find myself growing grim about the mouth; whenever it is a damp, drizzly November in my soul; whenever I find myself involuntarily pausing before coffin warehouses, and bringing up the rear of every funeral I meet; and especially whenever my hypos get such an upper hand of me, that it requires a strong moral principle to prevent me from deliberately stepping into the street, and methodically knocking people's hats off—then, I account it high time to get to sea as soon as I can."
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/text')
def get_text():
    # 30% chance to try API, otherwise local
    if random.random() > 0.3:
        return jsonify({"content": random.choice(STORIES)["content"]})

    try:
        # Fetch book list
        with urllib.request.urlopen('https://gutendex.com/books?languages=en&sort=popular') as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if not data.get('results'):
            raise Exception("No results")
            
        random_book = random.choice(data['results'][:10])
        text_url = random_book['formats'].get('text/plain; charset=utf-8')
        
        if not text_url:
            raise Exception("No text format")
            
        # Fetch book content
        with urllib.request.urlopen(text_url) as text_response:
            text = text_response.read().decode('utf-8')
        
        return jsonify({"content": process_text(text)})
        
    except Exception as e:
        print(f"API fetch failed: {e}")
        return jsonify({"content": random.choice(STORIES)["content"]})

def process_text(text):
    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"
    
    start_index = text.find(start_marker)
    if start_index != -1:
        next_newline = text.find('\n', start_index)
        start_index = next_newline + 1 if next_newline != -1 else start_index + len(start_marker)
    else:
        start_index = 0
        
    end_index = text.find(end_marker)
    if end_index == -1:
        end_index = len(text)
        
    content = text[start_index:end_index]
    
    # Clean up whitespace
    content = ' '.join(content.split())
    
    # Get a random chunk if it's long
    if len(content) > 600:
        random_start = random.randint(0, len(content) - 600)
        chunk_start = content.find('.', random_start)
        
        if chunk_start == -1:
            chunk_start = random_start
        else:
            chunk_start += 1
            
        return content[chunk_start:chunk_start + 500].strip()
        
    return content

if __name__ == '__main__':
    app.run(debug=True, port=5000)
