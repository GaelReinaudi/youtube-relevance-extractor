from youtube_transcript_api import YouTubeTranscriptApi
import openai

from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.
# Configure your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_summary(text):
    # Split the input text into chunks to fit the model's maximum context length
    chunks = [text[i : i + 4096] for i in range(0, len(text), 4096)]

    messages = []
    for i, chunk in enumerate(chunks):
        # The system message is sent only for the first chunk
        if i == 0:
            messages.append(
                {
                    "role": "system",
                    "content": """
this text comes from YouTube subtitles. 
please extract the factual information from it, eliminating any unnecessary chatter.
For example, consider the following subtitles: 
"Today, I'm going to show you my favorite carrot cake recipe. I just love how the sweetness of the carrots blends with the creaminess of the cheese frosting. First, preheat your oven to 350 degrees. While that's warming up, you can start by grating 0,2 cups of carrots, my god i love this smell, suscribe folks!that's important! add 1 cup of water slowly, i mean after 5min, oh that's nice, now add 0,5 cup of milk..." 
The result would be:
"Preheat oven to 350 degrees. 
 - 1 Grate 1 cup of carrots.
 - 2 after 5min add 1 cup of water,
 - 3 add 0,5 cup of milk,
 - 4 credibility: 3/10 because too little carrots."

Here is another example, if the subtitles were : 
"comment démarrer une chaîne YouTube qui gagne réellement de l'argent, en utilisant uniquement Ai et nous allons automatiser l'ensemble du processus de création vidéo, c'est un fait je suis celui qui va vous aider, de l'écriture du script à la voix off,je me servirai du site offvox.com lié à python en trouvant les visuels et tout le reste entre et par  À la fin de cette vidéo, nous aurons construit une machine YouTube lucrative, abonnez-vous pour connaitre le script."
The result would be:
"carefull! NO factual infos.
 - 1 traduit.com linked to python 
 - 2 credibility: 1/10 because no tangible examples, no practical advice to make money with youtube&AI&offvox, just subscription requests.' Limit the credibility line to a maximum of 16 words. result MUST BE ALWAYS IN OREDERED LIST"
""",
                }
            )

        messages.append({"role": "user", "content": chunk})

    # Use ChatGPT to generate a summary
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    return completion.choices[-1].message['content']


# Le reste de votre code ici...


while True:
    # Request the user to provide the list of videos
    video_list_input = input(
        "Veuillez fournir la liste des vidéos (séparées par des virgules) : "
    )
    video_list = [video.strip() for video in video_list_input.split(',')]

    # Iterate over the list of videos
    for video_url in video_list:
        try:
            # Extract video ID from the URL
            video_id = video_url.split('=')[-1]

            if captions := YouTubeTranscriptApi.get_transcript(video_id):
                print(f"Sous-titres disponibles pour la vidéo {video_url}:")
                all_text = ""
                for caption in captions:
                    text = caption['text']
                    all_text += text + " "

                # Split the concatenated subtitles into chunks
                text_chunks = [
                    all_text[i: i + 4096] for i in range(0, len(all_text), 4096)
                ]

                print("Résumés des sous-titres :")
                for chunk in text_chunks:
                    # Generate a summary using ChatGPT for each chunk
                    summary = generate_summary(chunk)
                    print(summary)

            else:
                print(f"Aucun sous-titre disponible pour la vidéo {video_url}")

        except Exception as e:
            print(
                f"Une erreur s'est produite lors de la récupération des sous-titres pour la vidéo {video_url}: {str(e)}"
            )

    while True:
        choix = input(
            "Avez-vous d'autres vidéos dont extraire les sous-titres ? Tapez O pour oui, N pour non : "
        )
        if choix.lower() in ['o', 'n']:
            break
        else:
            print("Veuillez entrer une valeur valide (O pour oui, N pour non).")

    if choix.lower() != 'o':
        break
