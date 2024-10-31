import gradio as gr
from dotenv import load_dotenv
from gradio import ChatMessage
from deepgram import DeepgramClient, SpeakOptions
from setup import Script, Vector_db, Speech_Text
from langchain_openai import ChatOpenAI
load_dotenv()

bot = Script()
vector = Vector_db()
transcriptor = Speech_Text()
pdf_uploaded = False
output_id = None

# Function to generate chatbot response
def generate_response(chat_history: list[ChatMessage], id=None):
    user_input = chat_history[-1]["content"]
    if len(chat_history) > 1:
        chat = bot.history(chat_history[:-2])
    else:
        chat = ''
    if id is not None:
        rag_chain, question = bot.gpt_loaders_id(user_input, chat, id)
    else:
        rag_chain, question = bot.gpt_loaders(user_input, chat)
    return rag_chain.invoke(question)


def process(audio, input_text, pdfs, chat_history: list[ChatMessage]):
    global pdf_uploaded, input_pdf, output_id
    if pdfs is not None and not pdf_uploaded:
        pdf_uploaded = True
        pdf_path = pdfs.name
        output_id = vector.upload_pdfs_user(pdf_path)
        # print(output_id)
    if pdfs is None:
        pdf_uploaded = False
        output_id = None
        # print(output_id)
    if audio is not None:
        transcript = transcriptor.get_transcript(audio)
        chat_history.append({"role": "user", "content": transcript})

    elif input_text:
        # print(input_text)
        chat_history.append({"role": "user", "content": input_text})

    else:
        response = 'Provide a query text or an audio to query.'
        chat_history.append({"role": "assistant", "content": response})
        audio_data = transcriptor.speech_synthesis(response)
        return audio_data, chat_history

    response = generate_response(chat_history, output_id)
    chat_history.append({"role": "assistant", "content": response})
    audio_data = transcriptor.speech_synthesis(response)
    return audio_data, chat_history

# Create Gradio Blocks interface
with gr.Blocks() as demo:
    gr.Markdown("""
    # 🎤 Welcome to the ChatBot
    This Bot has a Knowledge base on Indian Taxation Data by default. It allows you to chat with an AI assistant using either **text** or **voice**.<br>You can upload your own PDF data as knowledge base in the **upload a PDF** and can talk to your data seamlessly.
    """)
    with gr.Row():
        with gr.Column(scale=1, min_width=300):
            input_pdf = gr.File(label="Upload PDF", file_types=[".pdf"], file_count='single')
            gr.Markdown("_Upload a PDF to chat with it!_", visible=not pdf_uploaded)
    
    with gr.Row():
        chatbot = gr.Chatbot(label="Chatbot Conversation", type="messages", bubble_full_width=True, show_copy_button=True, autoscroll=True)
    
    with gr.Row():
        input_textbox = gr.Textbox(label="Input Text", placeholder="Type your message here...")
        input_audio = gr.Audio(label="Input Audio", sources="microphone", type="numpy")
    
    process_button = gr.Button("Submit Query")
    output_audio = gr.Audio(label="Assistant's Response Audio", interactive=False, autoplay=True)

    process_button.click(
        fn=process,
        inputs=[input_audio, input_textbox, input_pdf, chatbot],
        outputs=[output_audio, chatbot]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0",server_port=80)